from __future__ import annotations

import logging
import os
import signal
import subprocess
import sys
import threading
import time
from datetime import (
    datetime,
    timedelta,
)
from subprocess import PIPE
from typing import IO

import exasol.bucketfs as bfs
import mlflow
import pytest
import sklearn  # type: ignore

from exasol.mlflow_plugin.artifacts.bucketfs_connector import Connector

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


class MlflowServer:
    def __init__(self, command: list[str]):
        self.command = command
        self._proc: subprocess.Popen | None = None
        self._started: bool = False
        self._thread: threading.Thread | None = None

    def listen(self, text: str) -> None:
        if not self._proc:
            return
        pipe = self._proc.stderr
        if not isinstance(pipe, IO):
            return
        with pipe:
            for data in iter(pipe.readline, b""):
                line = data.decode()
                print(line, end="", file=sys.stderr)
                if text in line:
                    self._started = True

    def wait_for_message(self, text: str) -> MlflowServer:
        """
        See the developer guide for an explanation of kwarg
        ``preexec_fn=os.setsid`` and calling ``os.killpg()``.
        """

        pretty = " ".join(self.command).replace(" --", "\n    --")
        LOG.info("Starting MLflow server with\n  %s", pretty)
        self._proc = subprocess.Popen(
            self.command,
            stderr=PIPE,
            text=False,
            preexec_fn=os.setsid,  # create a separate process group
        )
        self._thread = threading.Thread(target=self.listen, args=(text,))
        self._thread.start()
        timeout = datetime.now() + timedelta(seconds=10)
        while datetime.now() < timeout:
            if self._started:
                break
            time.sleep(0.3)
        return self

    def stop(self) -> None:
        if not self._proc:
            return
        p = self._proc
        LOG.info(f"Stopping MLflow server process {p.pid}")
        os.killpg(os.getpgid(p.pid), signal.SIGTERM)
        p.wait()
        if self._thread:
            self._thread.join()
            self._thread = None


@pytest.fixture
def mlflow_server(tmp_path, connector: Connector):
    path = tmp_path / "mlflow.db"
    port = 5000
    command = [
        "mlflow",
        "server",
        "--backend-store-uri",
        f"sqlite:///{path}",
        "--port",
        str(port),
        "--default-artifact-root",
        connector.uri,
    ]
    # While tests are running, stderr needs to be consumed continuously.
    server = MlflowServer(command).wait_for_message("Application startup complete.")
    mlflow.set_tracking_uri(f"http://localhost:{port}")
    yield
    server.stop()


def log_sample_model() -> mlflow.models.model.ModelInfo:
    lr = sklearn.linear_model.LogisticRegression()
    return mlflow.sklearn.log_model(lr, name="my_first_logistic_regression")


def filenames(bfsloc: bfs.path.PathLike) -> set[str]:
    return {f.name for f in bfsloc.iterdir()}


def switch_uri(other: Connector, uri: str) -> Connector:
    return Connector(
        uri,
        other.username,
        other.password,
        other.ssl_cert_validation,
    )


@pytest.mark.parametrize("cls, mlflow_package", [
    (sklearn.linear_model.LogisticRegression, mlflow.sklearn),
])
def test_round_trip(cls, mlflow_package, mlflow_server, connector):
    """
    Parameters:
    * cls: Model class to instantiate for the round trip
    * mlflow_package: mlflow package to use for logging and loading the model instance.
    """

    model_name = f'{cls.__module__}.{cls.__name__}'.replace(".", ">")
    info = mlflow_package.log_model(cls(), name=model_name)
    LOG.info(f'info.model_uri = {info.model_uri}')
    loaded = mlflow_package.load_model(info.model_uri)
    LOG.info(f'{type(loaded).__name__}')
    assert type(loaded) == cls


def test_log_model(mlflow_server, connector):
    info = log_sample_model()
    other = switch_uri(connector, info.artifact_path)
    expected = {
        "conda.yaml",
        "python_env.yaml",
        "model.pkl",
        "MLmodel",
        "requirements.txt",
    }
    actual = filenames(other.bucketfs_location)
    assert actual == expected
