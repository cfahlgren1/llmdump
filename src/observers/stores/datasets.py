import atexit
import hashlib
import json
import os
import tempfile
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional

from datasets import Dataset
from huggingface_hub import CommitScheduler, login, metadata_update, whoami
from PIL import Image

from observers.stores.base import Store

if TYPE_CHECKING:
    from observers.observers.base import Record


def push_to_hub(self, *args, **kwargs):
    """Push pending changes to the Hugging Face Hub"""

    data = []
    for json_file in Path(self.folder_path).rglob("*.json"):
        with open(json_file) as f:
            for line in f:
                data.append(json.loads(line))

    dataset = Dataset.from_list(data)
    if "file_name" in dataset.column_names:

        def add_image_from_file_name(batch: List[Dict]):
            batch["image"] = [
                Image.open(Path(self.folder_path) / file_name)
                for file_name in batch["file_name"]
            ]
            return batch

        dataset = dataset.map(add_image_from_file_name, batched=True)
        dataset = dataset.remove_columns(["file_name"])
        dataset = dataset.rename_column("image", "file_name")

    dataset.push_to_hub(repo_id=self.repo_id, token=self.token, private=self.private)


CommitScheduler.push_to_hub = push_to_hub


@dataclass
class DatasetsStore(Store):
    """
    Datasets store
    """

    org_name: Optional[str] = field(default=None)
    repo_name: Optional[str] = field(default=None)
    folder_path: Optional[str] = field(default=None)
    every: Optional[int] = field(default=5)
    path_in_repo: Optional[str] = field(default=None)
    revision: Optional[str] = field(default=None)
    private: Optional[bool] = field(default=None)
    token: Optional[str] = field(default=None)
    allow_patterns: Optional[List[str]] = field(default=None)
    ignore_patterns: Optional[List[str]] = field(default=None)
    squash_history: Optional[bool] = field(default=None)

    _filename: Optional[str] = field(default=None)
    _scheduler: Optional[CommitScheduler] = None
    _temp_dir: Optional[str] = field(default=None, init=False)

    def __post_init__(self):
        """Initialize the store and create temporary directory"""
        if self.ignore_patterns is None:
            self.ignore_patterns = ["*.json"]

        try:
            whoami(token=self.token or os.getenv("HF_TOKEN"))
        except Exception:
            login()

        if self.folder_path is None:
            self._temp_dir = tempfile.mkdtemp(prefix="observers_dataset_")
            self.folder_path = self._temp_dir
            atexit.register(self._cleanup)
        else:
            os.makedirs(self.folder_path, exist_ok=True)

    def _cleanup(self):
        """Clean up temporary directory on exit"""
        if self._temp_dir and os.path.exists(self._temp_dir):
            import shutil

            shutil.rmtree(self._temp_dir)

    def _init_table(self, record: "Record"):
        repo_name = self.repo_name or "my-dataset"
        org_name = self.org_name or whoami(token=self.token)["name"]
        repo_id = f"{org_name}/{repo_name}"
        self._filename = f"{record.table_name}_{uuid.uuid4()}.json"
        self._scheduler = CommitScheduler(
            repo_id=repo_id,
            folder_path=self.folder_path,
            every=self.every,
            path_in_repo=self.path_in_repo,
            repo_type="dataset",
            revision=self.revision,
            private=self.private,
            token=self.token,
            allow_patterns=self.allow_patterns,
            ignore_patterns=self.ignore_patterns,
            squash_history=self.squash_history,
        )
        self._scheduler.private = self.private
        metadata_update(
            repo_id=repo_id,
            metadata={"tags": ["observers", record.table_name.split("_")[0]]},
            repo_type="dataset",
            token=self.token,
        )

    @classmethod
    def connect(
        cls,
        org_name: Optional[str] = None,
        repo_name: Optional[str] = None,
        folder_path: Optional[str] = None,
        every: Optional[int] = 5,
        path_in_repo: Optional[str] = None,
        revision: Optional[str] = None,
        private: Optional[bool] = None,
        token: Optional[str] = None,
        allow_patterns: Optional[List[str]] = None,
        ignore_patterns: Optional[List[str]] = None,
        squash_history: Optional[bool] = None,
    ) -> "DatasetsStore":
        """Create a new store instance with optional custom path"""
        return cls(
            org_name=org_name,
            repo_name=repo_name,
            folder_path=folder_path,
            every=every,
            path_in_repo=path_in_repo,
            revision=revision,
            private=private,
            token=token,
            allow_patterns=allow_patterns,
            ignore_patterns=ignore_patterns,
            squash_history=squash_history,
        )

    def add(self, record: "Record"):
        """Add a new record to the database"""
        if not self._scheduler:
            self._init_table(record)

        with self._scheduler.lock:
            with (self._scheduler.folder_path / self._filename).open("a") as f:
                record_dict = asdict(record)
                record_dict["synced_at"] = None

                for json_field in record.json_fields:
                    if record_dict[json_field]:
                        record_dict[json_field] = json.dumps(record_dict[json_field])

                for image_field in record.image_fields:
                    if record_dict[image_field]:
                        # Create images folder if it doesn't exist
                        image_folder = self._scheduler.folder_path / "images"
                        image_folder.mkdir(exist_ok=True)

                        # Save image with unique filename based on content
                        filtered_dict = {
                            k: v
                            for k, v in sorted(record_dict.items())
                            if k not in ["uri", image_field, "id"]
                        }
                        image_file_name = f"{hashlib.sha256(json.dumps(obj=filtered_dict, sort_keys=True).encode()).hexdigest()}.png"
                        image_path = image_folder / image_file_name
                        record_dict[image_field].save(image_path)

                        # Store relative path in record
                        record_dict[image_field] = str(
                            Path(image_folder.name) / image_file_name
                        )

                        record_dict["file_name"] = record_dict[image_field]

                if image_field in record_dict:
                    record_dict.pop(image_field)
                if "uri" in record_dict:
                    record_dict.pop("uri")

                # Replace empty dictionaries with None to avoid parqut errors
                for key, value in record_dict.items():
                    if value == {}:
                        record_dict[key] = None

                try:
                    f.write(
                        json.dumps(record_dict) + "\n"
                    )  # Add newline between records
                    f.flush()  # Ensure data is written to disk
                except Exception as e:
                    print(f"Failed to write record: {str(e)}")
                    raise
