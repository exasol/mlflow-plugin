Accessing the MLflow Backend Store Via an Exasol Virtual Schema
===============================================================

.. _virtual_schema:
https://docs.exasol.com/db/latest/database_concepts/virtual_schemas.htm

`Exasol Virtual Schemas <virtual_schema_>`_ can be used to map external data
sources to virtual tables that look like any regular Exasol tables and can be
queried as such.

Under some preconditions you can use an Exasol Virtual Schema for accessing
the MLflow Backend Store:

* You must be able to connect to the database backend used by the MLflow server.
* You must have appropriate credentials for accessing the database.
* MLflow must use a database backend for which a Virtual Schema implementation
  is available, e.g. PostgreSQL or MySQL, but not sqlite.

.. warning::

    Please note that the approach described here bypasses access control and
    permissions.

    This approach is therefore not recommended for production environments.

.. _postgres_virtual_schema: https://github.com/exasol/postgresql-virtual-schema/blob/main/doc/user_guide/postgresql_user_guide.md

Install the virtual schema, see the Postgres Virtual Schema `User Guide <postgres_virtual_schema_>`_.

* Download Postgres driver and virtual schema jar
* Upload the jar files to Exasol BucketFS incl. file ``settings.cfg``
* Create the following objects via Exasol SQL statements:

  * ``ADAPTER SCRIPT``
  * ``CONNECTION``
  * ``VIRTUAL SCHEMA``

After that you can inspect the virtual schema in your SQL Editor,
e.g. DbVisualizer:

.. image:: img/virtual-schema.png
