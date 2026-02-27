.. _developer_guide:

:octicon:`tools` Developer Guide
================================

How the MLflow Plugin works
---------------------------

This MLflow plugin uses dependencies ``mlflow`` and ``exasol-bucketfs``.

File ``pyproject.toml`` assigns URI schemes to the plugin:

.. literalinclude:: ../pyproject.toml
  :language: python
  :start-at: [tool.poetry.plugins."mlflow.artifact_repository"]
  :end-at: # end of plugin configuration

The plugin is implemented in ``exasol/mlflow_plugin/artifacts/repo.py``.

You can start the MLflow server with ``--default-artifact-root
exa+bfs://...``, see a complete command line given in the :ref:`User Guide
<starting the mlflow server>`.


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

The integration tests, therefore, use ``os.killpg()`` to terminate the entire
process group.

Additionally, the integration tests add kwarg ``preexec_fn=os.setsid`` when
starting the MLflow server. This runs the subprocess in its own *session*
preventing ``os.killpg()`` from terminating the ``pytest`` process itself.

Integration Tests
-----------------

MLFP integration tests automatically provision the following prerequisites via
fixtures:

* Run a Docker instance of Exasol for accessing the BucketFS
* Build a Script Language Container (SLC)
* Run an MLflow server

As these steps can be quite time-consuming, there are options to skip these
steps and reuse artifacts and services already provided on your local machine.

For reusing an existing database you can use the following pytest CLI options:

.. code-block:: shell

    pytest \
      --backend=onprem \
      --itde-db-version=external \
      --bucketfs-password "$BUCKETFS_PASSWORD"

See Pytest Plugin `Exasol-Backend <PYTBE_>`_.

.. _PYTBE: https://github.com/exasol/pytest-plugins/tree/main/pytest-backend#re-using-an-external-or-local-database

For skipping building and deploying the SLC you can add option ``--skip-slc``.

For reusing an already running instance of MLflow server you can add option

.. code-block:: shell

    pytest --mlflow-server http://localhost:5000
