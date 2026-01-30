.. _developer_guide:

:octicon:`tools` Developer Guide
================================

How the MLflow Plugin works
---------------------------

This MLflow plugin uses dependencies ``mlflow`` and ``exasol-bucketfs``.

File ``pyproject.toml`` assigns two URI schemes to the plugin:

.. code-block:: toml

   [tool.poetry.plugins."mlflow.artifact_repository"]
   "exa+bfs" = "exasol.mlflow_plugin.artifacts.repo:BucketFsArtifactRepo"
   "exa+bfss" = "exasol.mlflow_plugin.artifacts.repo:BucketFsArtifactRepo"

The plugin is implemented in ``exasol/mlflow_plugin/artifacts/repo.py``.

You can start the MLflow server with ``--default-artifact-root bfs://``.

MLflow Server Processes
-----------------------

The integration tests of the Exasol MLflow Plugin (MLFP) use a pytest fixture to
start an MLflow server.

The command ``mlflow server`` starts multiple processes:

.. code-block:: shell

    └─ mlflow server
       └─ --workers 4 mlflow.server.fastapi_app
          └─ main
             ├─ worker 1
             ├─ worker 2
             ├─ worker 3
             └─ worker 4

Terminating the MLflow server with ``Popen.kill()`` only affects the root
process, while ``fastapi``, ``main``, and the workers keep running.

The integration tests, therefore, use ``os.killpg()`` to terminate the complete
process group.

Additionally, the integration tests add kwarg ``preexec_fn=os.setsid`` when
starting the MLflow server. This runs the subprocess in its own *session*
preventing ``os.killpg()`` from terminating the ``pytest`` process itself.
