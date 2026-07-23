UDFs and Virtual Schema
=======================

Exasol's MLflow Plugin also contains :ref:`UDFs (User Defined Functions)
<rest_api>` and a Virtual Schema for accessing the MLflow REST API.

The UDFs use an Exasol Connection Object containing the MLflow tracking URI
and the credentials to access the MLflow REST API.

The Virtual Schema is based on the REST API UDFs and implemented itself as a
special UDF variant called an *Adapter Script*.

Additionally, the Virtual Schema requires to be *declared* via a separate SQL
statement.


Exaxol Connection Object
------------------------

.. literalinclude:: sql/connection.sql
  :caption: Exasol Connection Object
  :language: sql

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
     - The user name for logging in to the MLflow server, resp. its REST API.
   * - *<MLFLOW_PASSWORD>*
     - The password for logging in to the MLflow server, resp. its REST API.

For ``auth-type`` currently only value ``basic`` is supported.

Adapter Script
--------------

The following SQL statement creates the Adapter Script:

.. literalinclude:: sql/adapter_script.sql
  :caption: Adapter Script
  :language: sql


The Adapter Script requires the following parameters to be specified:

.. list-table::
   :header-rows: 1
   :widths: 10 20

   * - Parameter
     - Description
   * - *<ADAPTER_SCHEMA>*
     - The database schema to contain the Adapter Script.
   * - *<LANGUAGE_ALIAS>*
     - The language alias used when activating the MLflow SLC, see :ref:`install_slc`
   * - *<ADAPTER_NAME>*
     - The name of the Adapter Script to be used by the Virtual Schema.


Virtual Schema
--------------

.. literalinclude:: sql/virtual_schema.sql
  :caption: Virtual Schema Declaration
  :language: sql

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
   * - *<ADAPTER_NAME>*
     - The name of the Adapter Script.
   * - *<CONNECTION_NAME>*
     - The name of the connection to be used in the UDFs.
