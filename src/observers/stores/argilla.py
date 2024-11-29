from dataclasses import asdict, dataclass, field
from typing import TYPE_CHECKING, List, Optional

import argilla as rg
from argilla import Argilla

from observers.stores.base import Store

if TYPE_CHECKING:
    from observers.observers.base import Record


@dataclass
class ArgillaStore(Store):
    """
    Argilla store
    """

    api_url: Optional[str] = field(default=None)
    api_key: Optional[str] = field(default=None)
    dataset_name: Optional[str] = field(default=None)
    workspace_name: Optional[str] = field(default=None)

    _dataset: Optional[rg.Dataset] = None
    _dataset_keys: Optional[List[str]] = None
    _client: Optional[Argilla] = None

    def __post_init__(self) -> None:
        """Initialize the store"""
        self._client = Argilla(api_url=self.api_url, api_key=self.api_key)

    def _init_table(self, record: "Record") -> None:
        dataset_name = self.dataset_name or record.table_name
        workspace_name = self.workspace_name or self._client.me.username
        workspace = self._client.workspaces(name=workspace_name)
        if not workspace:
            workspace = self._client.workspaces.add(rg.Workspace(name=workspace_name))
        dataset = self._client.datasets(name=dataset_name, workspace=workspace_name)
        if not dataset:
            dataset = rg.Dataset(
                name=dataset_name,
                workspace=workspace_name,
                settings=record.argilla_settings(self._client),
                client=self._client,
            ).create()
        self._dataset = dataset
        dataset_keys = (
            [field.name for field in dataset.settings.fields]
            + [question.name for question in dataset.settings.questions]
            + [term.name for term in dataset.settings.metadata]
            + [vector.name for vector in dataset.settings.vectors]
        )
        self._dataset_keys = dataset_keys

    @classmethod
    def connect(
        cls,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        dataset_name: Optional[str] = None,
        workspace_name: Optional[str] = None,
    ) -> "ArgillaStore":
        """Create a new store instance with custom settings"""
        return cls(
            api_url=api_url,
            api_key=api_key,
            dataset_name=dataset_name,
            workspace_name=workspace_name,
        )

    def add(self, record: "Record") -> None:
        """Add a new record to the database"""
        if not self._dataset:
            self._init_table(record)

        record_dict = asdict(record)
        record_dict = {k: v for k, v in record_dict.items() if k in self._dataset_keys}
        self._dataset.records.log([record_dict])
