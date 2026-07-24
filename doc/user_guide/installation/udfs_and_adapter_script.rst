UDFs and Adapter Script
=======================

Exasol's MLflow Plugin contains :ref:`UDFs (User Defined Functions)
<rest_api>` and a Virtual Schema for accessing the MLflow REST API.  The
Virtual Schema is based on the REST API UDFs and implemented itself as a
special UDF variant called an *Adapter Script*.

SQL Statements
--------------

File :download:`deployment.sql` contains the SQL statements to create the UDFs
and the Adapter Script in the current database schema.

Additional Setup
----------------

The UDFs use an *Exasol Connection Object* containing the MLflow tracking URI
and the credentials to access the MLflow REST API.  Additionally, the Virtual
Schema requires a separate *declaration*.

See :ref:`connection_and_virtual_schema` for detailed instructions.
