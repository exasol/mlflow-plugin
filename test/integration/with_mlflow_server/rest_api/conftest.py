import os
from dataclasses import dataclass
from test.integration.with_mlflow_server.rest_api.gateway_rest_api import GatewayRestApi

import mlflow
import pytest
from sklearn.linear_model import LogisticRegression


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
