.. _connection_and_virtual_schema:

Connection and Virtual Schema
=============================

The UDFs use an Exasol Connection Object containing the MLflow tracking URI
and the credentials to access the MLflow REST API.

Additionally, the Virtual Schema requires to be *declared* via a separate SQL
statement.

Exaxol Connection Object
------------------------

.. code-block:: sql
   :caption: Exasol Connection Object

   CREATE OR REPLACE CONNECTION "<CONNECTION_NAME>"
     TO '<MLFLOW_TRACKING_URI>'
     USER '{"auth-type": "basic", "user": "<MLFLOW_USER_NAME>"}'
     IDENTIFIED BY '{"password": "<MLFLOW_PASSWORD>"}'

The Connection requires the following parameters to be specified:

.. list-table::
   :header-rows: 1
   :widths: 10 20

   * - Parameter
     - Description
   * - *<CONNECTION_NAME>*
     - The name of the connection to be used in the UDFs.
   * - *<MLFLOW_TRACKING_URI>*
     - The URL of the MLflow server serving the REST API endpoints.
   * - *<MLFLOW_USER_NAME>*
     - The user name for logging in to the MLflow REST API.
   * - *<MLFLOW_PASSWORD>*
     - The password for logging in to the MLflow REST API.

For ``auth-type`` currently only value ``basic`` is supported.

Virtual Schema Declaration
--------------------------

.. code-block:: sql
   :caption: Virtual Schema Declaration

   CREATE VIRTUAL SCHEMA "<VS_NAME>"
     USING "<ADAPTER_SCHEMA>"."MLFLOW_VIRTUAL_SCHEMA_ADAPTER"
     WITH
       CONNECTION_NAME = '<CONNECTION_NAME>'
       MAX_RESULTS = '100'

The Virtual Schema supports the following parameters:

.. list-table::
   :header-rows: 1
   :widths: 10 20

   * - Parameter
     - Description
   * - *<VS_NAME>*
     - Name of the virtual schema.
   * - *<ADAPTER_SCHEMA>*
     - The database schema containing the Adapter Script.
   * - *<CONNECTION_NAME>*
     - The name of the connection to be used in the UDFs.
