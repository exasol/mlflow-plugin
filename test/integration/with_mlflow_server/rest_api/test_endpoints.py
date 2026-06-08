import os
from dataclasses import dataclass

import mlflow
import pytest
from sklearn.linear_model import LogisticRegression

from exasol.mlflow_plugin import rest_api
from exasol.mlflow_plugin.rest_api import Endpoint
from exasol.mlflow_plugin.rest_api.streaming import DataStream


@dataclass
class SampleData:
    experiment_id: str = "0"
    run_name: str = "RRR_1"
    registered_model_name: str = "sample_registered_model"


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
def sample_data(monkeymodule, request, mlflow_server) -> SampleData:
    if server_url := request.config.getoption("--mlflow-server"):
        return SampleData()
    monkeymodule.setitem(os.environ, "MLFLOW_TRACKING_USERNAME", "admin")
    monkeymodule.setitem(os.environ, "MLFLOW_TRACKING_PASSWORD", "password1234")
    experiment_id = mlflow.create_experiment("exp5")
    # Create a run
    run_name = "sample_run"
    mlflow.start_run(experiment_id=experiment_id, run_name=run_name)
    mlflow.end_run()
    # create a model and register it
    registered_model_name = "sample_registered_model"
    mlflow.sklearn.log_model(
        LogisticRegression(),
        name="Cordoba",
        registered_model_name=registered_model_name,
    )

    return SampleData(
        experiment_id,
        run_name,
        registered_model_name,
    )


def data_stream(mlflow_server, endpoint: Endpoint) -> DataStream:
    return DataStream(
        base_uri=mlflow_server,
        auth=("admin", "password1234"),
        endpoint=endpoint,
    )


def test_runs_search(mlflow_server, sample_data):
    stream = data_stream(mlflow_server, rest_api.RUNS_SEARCH)
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
    mlflow_server, sample_data, endpoint, params
):
    stream = data_stream(mlflow_server, endpoint)
    params = params | {"name": sample_data.registered_model_name}
    rows = stream.retrieve(params)
    assert sample_data.registered_model_name in (r[0] for r in rows)


def test_model_versions_get_download_uri_and_artifacts(mlflow_server, sample_data):
    # Verify endpoint MODEL_VERSIONS_GET_DOWNLOAD_URI
    stream = data_stream(mlflow_server, rest_api.MODEL_VERSIONS_GET_DOWNLOAD_URI)
    params = {"name": sample_data.registered_model_name, "version": "1"}
    rows = stream.retrieve(params)
    uri = next(rows)[0]
    assert uri.startswith("mlflow-artifacts:/")

    # Verify endpoint ARTIFACTS_LIST
    stream = data_stream(mlflow_server, rest_api.ARTIFACTS_LIST)
    path = uri.replace("mlflow-artifacts:/", "")
    params = {"path": path}
    rows = stream.retrieve(params)
    assert "model.pkl" in (r[0] for r in rows)
