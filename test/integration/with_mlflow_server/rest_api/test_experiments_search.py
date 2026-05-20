import mlflow
import pytest

from exasol.mlflow_plugin.rest_api import ExperimentsSearch

import pytest

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
def experiments_search(mlflow_server, sample_data):
    return ExperimentsSearch(f"{mlflow_server}/api/2.0/mlflow/")


def test_deleted(experiments_search):
    params = {"view_type": "DELETED_ONLY"}
    actual = list(experiments_search.call(params))
    count_deleted =sum(1 for a in actual if a[3] == "deleted")
    assert count_deleted > 0


def test_tags(experiments_search):
    params = {"filter": f"name = '{TAGGED_EXPERIMENT}'"}
    actual = list(experiments_search.call(params))
    tags = [tuple(el[-2:]) for el in actual]
    assert tags == SAMPLE_TAGS


def test_other_options(experiments_search):
    """
    Tests other options max_results, filter, order_by.
    """
    params = {
        "max_results": 1,
        "filter": "name LIKE 'a-%'",
        "order_by": ["name"],
    }
    actual = experiments_search.call(params)
    assert [el[1] for el in actual] == ["a-1", "a-2"]
