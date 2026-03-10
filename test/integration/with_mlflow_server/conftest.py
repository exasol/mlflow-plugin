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
from typing import (
    IO,
    Generator,
)

import mlflow
import pytest
import sklearn

from exasol.mlflow_plugin.artifacts.bucketfs_connector import Connector

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logging.getLogger("exasol.bucketfs").setLevel(logging.WARNING)


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


@pytest.fixture(scope="module")
def mlflow_server(tmp_path_factory, connector: Connector, request) -> Generator[str, None, None]:
    if server_url := request.config.getoption("--mlflow-server"):
        LOG.info(f"Reusing MLflow server already running at {server_url}")
        mlflow.set_tracking_uri(server_url)
        yield server_url
        return

    path = tmp_path_factory.mktemp("data") / "mlflow.db"
    port = 5000
    command = [
        "mlflow",
        "server",
        "--backend-store-uri",
        f"sqlite:///{path}",
        "--port",
        str(port),
        # Option "--default-artifact-root" connector.uri has been removed in
        # favor of fixture bfs_experiment creating a dedidated experiment
        # using the BucketFS as artifact store.
    ]
    # While tests are running, stderr needs to be consumed continuously.
    server = MlflowServer(command).wait_for_message("Application startup complete.")
    tracking_uri = f"http://localhost:{port}"
    mlflow.set_tracking_uri(tracking_uri)
    yield tracking_uri
    server.stop()


@pytest.fixture(scope="module")
def bfs_experiment(connector: Connector) -> str:
    name = "BFS-Experiment"
    mlflow.create_experiment(name, artifact_location=connector.uri)
    mlflow.set_experiment(name)
    return name


@pytest.fixture(scope="module")
def logged_sample_model(mlflow_server, bfs_experiment: str) -> str:
    """
    Return artifact URI, example:
      exa+bfs://localhost:2580/bfsdefault/default/
      0/models/m-f9938cdb7b3d4035add2cf24a6c67fad/artifacts
    """
    model = sklearn.linear_model.LogisticRegression()
    info = mlflow.sklearn.log_model(model, name="Example-Model")
    return info.artifact_path
