from pathlib import Path

import pytest
from datasets import DatasetDict, load_dataset


@pytest.fixture
def dataset_path() -> str:
    return str(Path(__file__).parents[1] / "economy-watchers-survey.py")


@pytest.mark.parametrize("dataset_name", ("current", "future"))
def test_load_dataset(dataset_path: str, dataset_name: str) -> None:
    print(dataset_path)
    dsd: DatasetDict = load_dataset(path=dataset_path, name=dataset_name)
    _ = dsd["train"]
    _ = dsd["test"]
