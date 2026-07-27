Generated Files
===============

The MLflow Plugin provides two Nox sessions for generating files:

* ``nox -s code:generate`` generates file
  ``exasol/mlflow_plugin/deploy/extension.sql``, containing SQL statements for
  deploying the REST API UDFs and the Adapter Script for the Virtual Schema.

* ``nox -s docs:update`` generates file
  ``doc/user_guide/access_mlflow/rest_endpoints.rst``, describing the UDFs for
  accessing the MLflow REST API in the User Guide.
