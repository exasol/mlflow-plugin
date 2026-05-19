import mlflow
import pytest

from exasol.mlflow_plugin.rest_api import ExperimentsSearch


@pytest.fixture(scope="module")
def xmlflow_server():
    return f"http://localhost:5000"


@pytest.fixture(scope="module")
def rest_api_uri(mlflow_server):
    return f"{mlflow_server}/api/2.0/mlflow/"


def test_deleted(rest_api_uri):
    id = mlflow.create_experiment("deleted")
    mlflow.delete_experiment(id)
    params = {"view_type": "DELETED_ONLY"}
    endpoint = ExperimentsSearch(rest_api_uri, params)
    active = [el for el in endpoint.result() if el["lifecycle_stage"] == "deleted"]
    assert len(active) > 0


def test_tags(rest_api_uri):
    id = mlflow.create_experiment("zzz")
    mlflow.set_experiment("zzz")
    tags = {"T1": "V1", "T2": "V2"}
    mlflow.set_experiment_tags(tags)
    params = {"filter": "name = 'zzz'"}
    endpoint = ExperimentsSearch(rest_api_uri, params)
    actual = list(endpoint.result())
    assert len(actual) == 2
    actual_tags = {el["tag_key"]: el["tag_value"] for el in actual}
    assert actual_tags == tags


def test_other_options(rest_api_uri):
    """
    Tests other options max_results, filter, order_by.
    """
    mlflow.create_experiment("a-1")
    mlflow.create_experiment("a-2")
    mlflow.create_experiment("z-1")
    mlflow.create_experiment("z-2")
    params = {
        "max_results": 1,
        "filter": "name LIKE 'a-%'",
        "order_by": ["name"],
    }
    endpoint = ExperimentsSearch(rest_api_uri, params)
    assert [el["name"] for el in endpoint.result()] == ["a-1", "a-2"]
