import mlflow
import pytest

from exasol.mlflow_plugin.rest_api import EXPERIMENTS_SEARCH
from exasol.mlflow_plugin.rest_api.streaming import DataStream

TAGGED_EXPERIMENT = "zzz"
SAMPLE_TAGS = [("T1", "V1"), ("T2", "V2")]


@pytest.fixture(scope="module")
def sample_data(request, mlflow_server):
    if server_url := request.config.getoption("--mlflow-server"):
        return
    # Deleted experiment
    id = mlflow.create_experiment("deleted")
    mlflow.delete_experiment(id)
    # Tagged experiment
    mlflow.create_experiment(TAGGED_EXPERIMENT)
    mlflow.set_experiment(TAGGED_EXPERIMENT)
    mlflow.set_experiment_tags(dict(SAMPLE_TAGS))
    # Experiments with different prefixes for filtering
    mlflow.create_experiment("a-1")
    mlflow.create_experiment("a-2")
    mlflow.create_experiment("z-1")
    mlflow.create_experiment("z-2")


@pytest.fixture
def experiments_search(mlflow_server, sample_data) -> DataStream:
    return DataStream(
        base_uri=f"{mlflow_server}/api/2.0/mlflow",
        auth=("admin", "password1234"),
        endpoint=EXPERIMENTS_SEARCH,
    )


def test_deleted(experiments_search):
    actual = experiments_search.retrieve({"view_type": "DELETED_ONLY"})
    count_deleted = sum(1 for a in actual if a[3] == "deleted")
    assert count_deleted > 0


def test_tags(experiments_search):
    filter = f"name = '{TAGGED_EXPERIMENT}'"
    actual = experiments_search.retrieve({"filter": filter})
    tags = [tuple(el[-2:]) for el in actual]
    assert tags == SAMPLE_TAGS


def test_other_options(experiments_search):
    """
    Tests other options max_results, filter, order_by.
    """
    params = {
        "filter": "name LIKE 'a-%'",
        "order_by": ["name"],
        "max_results": 1,
    }
    actual = experiments_search.retrieve(params)
    names = [el[1] for el in actual]
    assert names == ["a-1", "a-2"]
