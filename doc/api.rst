.. _api:

:octicon:`cpu` API Reference
=============================

.. autodata:: exasol.mlflow_plugin.env_vars.ENV_BUCKETFS_USER
.. autodata:: exasol.mlflow_plugin.env_vars.ENV_BUCKETFS_PASSWORD
.. autodata:: exasol.mlflow_plugin.env_vars.ENV_SSL_CERT_VALIDATION

.. autofunction:: exasol.mlflow_plugin.artifacts.bucketfs_connector.udf_path
.. autofunction:: exasol.mlflow_plugin.artifacts.bucketfs_connector.local_path_or_uri
.. autofunction:: exasol.mlflow_plugin.artifacts.bucketfs_connector.load_model_with_fallback

.. autoclass:: exasol.mlflow_plugin.artifacts.bucketfs_connector.BfsSpecError
.. autoclass:: exasol.mlflow_plugin.artifacts.bucketfs_connector.EnvError
.. autoclass:: exasol.mlflow_plugin.artifacts.bucketfs_connector.ParseError
.. autoclass:: exasol.mlflow_plugin.artifacts.bucketfs_connector.Connector
   :members:
