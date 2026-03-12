How the MLflow Plugin works
===========================

This MLflow plugin uses dependencies ``mlflow`` and ``exasol-bucketfs``.

File ``pyproject.toml`` assigns URI schemes to the plugin:

.. literalinclude:: ../../pyproject.toml
  :language: toml
  :start-at: [tool.poetry.plugins."mlflow.artifact_repository"]
  :end-before: # end of plugin configuration

The plugin is implemented in ``exasol/mlflow_plugin/artifacts/repo.py``.

You can start the MLflow server with ``--default-artifact-root
exa+bfs://...``, see a complete command line given in the :ref:`User Guide
<starting the mlflow server>`.
