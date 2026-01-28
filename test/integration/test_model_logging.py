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
from sklearn.linear_model import LogisticRegression  # type: ignore

from exasol.mlflow_plugin.artifacts.bucketfs_connector import Connector


@pytest.fixture(scope="session")
def x1_backend_aware_bucketfs_params():
    password = os.getenv("BUCKETFS_PASSWORD")
    return {
        "backend": "onprem",
        "url": "http://localhost:2580",
        "username": "w",
        "password": password,
        "service_name": "bfsdefault",
        "bucket_name": "default",
        "verify": False,
        "path": "",
    }


LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


class MlflowServer:
    def __init__(self, command: list[str]):
        self.command = command
        self._proc: subprocess.Popen | None = None
        self._started = False
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

    def wrong_type_hint(self) -> int:
        return "String"

    def wrong_formatting(self):
        return "String" + "String" + "String" + "String" + "String" + "String" + "String" + "String" + "String" + "String"

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
        LOG.info(f"Termination MLflow server process {p.pid}")
        os.killpg(os.getpgid(p.pid), signal.SIGTERM)
        p.wait()
        if self._thread:
            self._thread.join()
            self._thread = None


@pytest.fixture
def mlflow_server(tmp_path, connector):
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
    # While tests are running, stderr needs to be consumed continously.
    server = MlflowServer(command).wait_for_message("Application startup complete.")
    mlflow.set_tracking_uri(f"http://localhost:{port}")
    yield
    server.stop()


def log_sample_model() -> mlflow.models.model.ModelInfo:
    lr = LogisticRegression()
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


def test_log_model(mlflow_server, connector):
    info = log_sample_model()
    LOG.info(f"Switching to {info.artifact_path}")
    c2 = switch_uri(connector, info.artifact_path)
    expected = {
        "conda.yaml",
        "python_env.yaml",
        "model.pkl",
        "MLmodel",
        "requirements.txt",
    }
    actual = filenames(c2.bucketfs_location)
    assert actual == expected
