import logging
import os
import re
import signal
import subprocess
import sys
import threading
from typing import IO
import time
from datetime import (
    datetime,
    timedelta,
)
from subprocess import PIPE

import exasol.bucketfs as bfs
import mlflow
import pytest
from sklearn.linear_model import LogisticRegression # type: ignore

from exasol.mlflow_plugin.artifacts.bucketfs_connector import Connector
from exasol.mlflow_plugin.experiment import training_data as td

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


class DotAccess:
    def __init__(self, content):
        self._data = content

    def __getattr__(self, key):
        return self._data[key]


@pytest.fixture(scope="session")
def backend_aware_bucketfs_params():
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


@pytest.fixture(scope="session")
def connector(backend_aware_bucketfs_params) -> Connector:
    p = DotAccess(backend_aware_bucketfs_params)
    if p.backend == "saas":
        scheme = "exa+saas"
        raise NotImplementedError(f"Backend {p.backend}")

    prefix = re.sub(r"^http(s?)://", "exa+bfs\\1://", p.url)
    uri = f"{prefix}/{p.service_name}/{p.bucket_name}/{p.path}"
    return Connector(uri, p.username, p.password, p.verify)


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

    def wait_for_message(self, text: str) -> None:
        """
        See the developer guide for an explanation of kwarg
        ``preexec_fn=os.setsid`` and calling ``os.killpg()``.
        """

        LOG.info("Starting MLflow server with\n  %s", " ".join(self.command))
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
                return
            time.sleep(0.3)

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
def mlflow_server(tmp_path, connector, monkeypatch):
    for k, v in connector.env.items():
        monkeypatch.setitem(os.environ, k, v)
    path = tmp_path / "mlflow.db"
    command = [
        "mlflow",
        "server",
        "--backend-store-uri",
        f"sqlite:///{path}",
        "--port",
        "5000",
        "--default-artifact-root",
        connector.uri,
    ]

    # While tests are running, stderr needs to be consumed continously.
    monitor = MlflowServer(command)
    monitor.wait_for_message("Application startup complete.")
    yield
    monitor.stop()


def log_sample_model() -> mlflow.models.model.ModelInfo:
    lr = LogisticRegression()
    return mlflow.sklearn.log_model(lr, name="my_first_logistic_regression")


def filenames(bfsloc: bfs.path.PathLike) -> set[str]:
    return {f.name for f in bfsloc.iterdir()}


def test_log_model(mlflow_server, connector):
    info = log_sample_model()
    connector = connector.for_uri(info.artifact_path)
    expected = {
        "conda.yaml",
        "python_env.yaml",
        "model.pkl",
        "MLmodel",
        "requirements.txt",
    }
    actual = filenames(connector.bucketfs_location)
    assert actual == expected
