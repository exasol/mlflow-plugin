.. _developer_guide:

:octicon:`tools` Developer Guide
================================

The integration tests of Exasol MLflow Plugin (MLFP) use a pytest fixture to
start an MLflow server.

The command ``mlflow server`` starts multiple processes

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

The integration tests therefore use ``os.killpg()`` to terminate the complete
process group.

Additionally, the integration tests add kwarg ``preexec_fn=os.setsid`` when
starting the MLflow server. This runs the subprocess in its own *session*
preventing ``os.killpg()`` to terminate the ``pytest`` process itself.
