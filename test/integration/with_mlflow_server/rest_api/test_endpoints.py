import pytest

from exasol.mlflow_plugin import rest_api
from exasol.mlflow_plugin.rest_api import Endpoint
from exasol.mlflow_plugin.rest_api.streaming import DataStream


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
    assert "model.skops" in (r[0] for r in rows)


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
