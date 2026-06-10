import os
from dataclasses import dataclass
from test.integration.with_mlflow_server.mlflow_connection import MLflowConnection
from test.integration.with_mlflow_server.rest_api.gateway_rest_api import GatewayRestApi
from typing import Callable

import mlflow
import pytest
import requests
from _pytest.monkeypatch import MonkeyPatch
from sklearn.linear_model import LogisticRegression

from exasol.mlflow_plugin import rest_api
from exasol.mlflow_plugin.rest_api import Endpoint
from exasol.mlflow_plugin.rest_api.data import JsonObject
from exasol.mlflow_plugin.rest_api.rest_api import RestApiError
from exasol.mlflow_plugin.rest_api.streaming import DataStream


@dataclass
class SampleData:
    experiment_id: str = "0"
    run_name: str = "RRR_1"
    registered_model_name: str = "sample_registered_model"
    gateway_model_definition_name: str = "sample_gateway_model_definition"
    gateway_endpoint_name: str = "sample_gateway_endpoint"


@pytest.fixture(scope="module")
def monkeymodule():
    """
    Instantiate monkeypatch with scope "module".
    """
    # See https://stackoverflow.com/questions/53963822
    from _pytest.monkeypatch import MonkeyPatch

    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture(scope="module")
def as_admin(monkeymodule, mlflow_connection):
    """
    Set environment variables to create resources for integration tests as
    admin.
    """
    env = {
        "MLFLOW_TRACKING_USERNAME": mlflow_connection.user,
        "MLFLOW_TRACKING_PASSWORD": mlflow_connection.password,
    }
    for k, v in env.items():
        monkeymodule.setitem(os.environ, k, v)


def create_gateway_data(
    mlflow_connection,
    model_definition_name: str,
    endpoint_name: str,
) -> None:
    api = GatewayRestApi(mlflow_connection)
    secret_id = api.create_secret("sample_secret")
    model_id = api.create_model_definition(secret_id, model_definition_name)
    api.create_endpoint(model_id, endpoint_name)


@pytest.fixture(scope="module")
def sample_data(as_admin, request, mlflow_connection) -> SampleData:
    if server_url := request.config.getoption("--mlflow-server"):
        return SampleData()
    exp = mlflow.set_experiment("exp5")
    # Create a run
    run_name = "sample_run"
    mlflow.start_run(experiment_id=exp.experiment_id, run_name=run_name)
    mlflow.end_run()
    # create a model and register it
    registered_model_name = "sample_registered_model"
    mlflow.sklearn.log_model(
        LogisticRegression(),
        name="Cordoba",
        registered_model_name=registered_model_name,
    )
    # create gateway sample data
    gateway_model_definition_name = "sample_gateway_model_definition"
    gateway_endpoint_name = "sample_gateway_endpoint"
    create_gateway_data(
        mlflow_connection,
        gateway_model_definition_name,
        gateway_endpoint_name,
    )

    return SampleData(
        exp.experiment_id,
        run_name,
        registered_model_name,
        gateway_model_definition_name,
        gateway_endpoint_name,
    )


def data_stream(mlflow_connection, endpoint: Endpoint) -> DataStream:
    return DataStream(
        base_uri=mlflow_connection.url,
        auth=mlflow_connection.auth,
        endpoint=endpoint,
    )


def test_runs_search(mlflow_connection, sample_data):
    stream = data_stream(mlflow_connection, rest_api.RUNS_SEARCH)
    params = {"experiment_ids": [sample_data.experiment_id]}
    rows = stream.retrieve(params)
    assert sample_data.run_name in (r[2] for r in rows)


@pytest.mark.parametrize(
    "endpoint, params",
    [
        (rest_api.REGISTERED_MODELS_SEARCH, {"filter": "name like 'sample_%'"}),
        (rest_api.REGISTERED_MODELS_GET_LATEST_VERSIONS, {}),
        (rest_api.REGISTERED_MODEL_GET, {}),
        (rest_api.MODEL_VERSIONS_SEARCH, {"filter": "name like 'sample_%'"}),
        (rest_api.MODEL_VERSIONS_GET, {"version": "1"}),
    ],
)
def test_registered_models_and_model_versions(
    mlflow_connection, sample_data, endpoint, params
):
    stream = data_stream(mlflow_connection, endpoint)
    params = params | {"name": sample_data.registered_model_name}
    rows = stream.retrieve(params)
    assert sample_data.registered_model_name in (r[0] for r in rows)


def test_model_versions_get_download_uri_and_artifacts(mlflow_connection, sample_data):
    # Verify endpoint MODEL_VERSIONS_GET_DOWNLOAD_URI
    stream = data_stream(mlflow_connection, rest_api.MODEL_VERSIONS_GET_DOWNLOAD_URI)
    params = {"name": sample_data.registered_model_name, "version": "1"}
    rows = stream.retrieve(params)
    uri = next(rows)[0]
    assert uri.startswith("mlflow-artifacts:/")

    # Verify endpoint ARTIFACTS_LIST
    stream = data_stream(mlflow_connection, rest_api.ARTIFACTS_LIST)
    path = uri.replace("mlflow-artifacts:/", "")
    params = {"path": path}
    rows = stream.retrieve(params)
    assert "model.pkl" in (r[0] for r in rows)


def test_list_gateway_model_definitions(sample_data, mlflow_connection) -> None:
    endpoint = rest_api.GATEWAY_MODEL_DEFINITIONS_LIST
    stream = data_stream(mlflow_connection, endpoint)
    rows = stream.retrieve({})
    assert sample_data.gateway_model_definition_name in (r[1] for r in rows)


def test_list_gateway_endpoints(sample_data, mlflow_connection) -> None:
    endpoint = rest_api.GATEWAY_ENDPOINTS_LIST
    stream = data_stream(mlflow_connection, endpoint)
    rows = stream.retrieve({})
    assert sample_data.gateway_endpoint_name in (r[1] for r in rows)
