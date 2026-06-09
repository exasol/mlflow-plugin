Accessing the MLflow Server
===========================

MLflow has various components, stores, and APIs.  The Exasol MLflow Plugin
allows to access two of them.

.. list-table::
    :header-rows: 1

    * - MLflow Component
      - Supported Access
    * - MLflow REST API
      - From within UDFs presenting the results as SQL tables.
    * - MLflow Backend Tracking Store
      - Via an Exasol Virtual Schema

Read about the details in the following sections

.. toctree::

   rest_api
   virtual_schema
