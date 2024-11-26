import os
import pytest
from unittest.mock import patch
from observers.stores.datasets import DatasetsStore


@pytest.fixture
def mock_whoami():
    with patch("observers.stores.datasets.whoami") as mock:
        mock.return_value = {}
        yield mock


@pytest.fixture
def mock_login():
    with patch("observers.stores.datasets.login") as mock:
        yield mock


@pytest.fixture
def datasets_store(mock_whoami, mock_login):
    store = DatasetsStore()
    yield store
    store._cleanup()


def test_temp_dir_creation(datasets_store):
    """Test that temporary directory is created during initialization"""
    assert datasets_store._temp_dir is not None
    assert os.path.exists(datasets_store._temp_dir)


def test_temp_dir_cleanup(datasets_store):
    """Test that temporary directory is cleaned up properly"""
    temp_dir = datasets_store._temp_dir
    assert os.path.exists(temp_dir)

    datasets_store._cleanup()
    assert not os.path.exists(temp_dir)


def test_folder_path_defaults_to_temp_dir(datasets_store):
    """Test that folder_path defaults to temp_dir when not provided"""
    assert datasets_store.folder_path == datasets_store._temp_dir


def test_custom_folder_path(mock_whoami, mock_login, tmp_path):
    """Test that custom folder_path is respected and not deleted during cleanup"""
    custom_path = str(tmp_path / "custom_datasets")
    os.makedirs(custom_path, exist_ok=True)

    store = DatasetsStore(folder_path=custom_path)
    assert store.folder_path == custom_path
    assert store._temp_dir is None

    store._cleanup()
    assert os.path.exists(
        custom_path
    ), "Custom folder should not be deleted during cleanup"
