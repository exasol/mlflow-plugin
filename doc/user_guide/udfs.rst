Accessing Artifacts from Within a UDF
=====================================

Using the Exasol MLflow Plugin significantly speeds up loading MLflow models
in Exasol `UDFs
<https://docs.exasol.com/db/latest/database_concepts/udf_scripts.htm>`_.

Such a UDF could be defined like this

.. code-block:: sql

    --/
    CREATE OR REPLACE MLFLOW_SLC
       SCALAR SCRIPT "<SCHEMA>"."<UDF_NAME>"(uri VARCHAR(2000))
       RETURNS BOOL AS
    import mlflow
    from exasol.mlflow_plugin.artifacts.bucketfs_connector import Connector
    def run(ctx):
        con = Connector(ctx.uri, "", "", False)
        path = con.bucketfs_location.as_udf_path()
        model = mlflow.sklearn.load_model(path)
        #--
        #-- your implementation using the model goes here
        #--
        return True
    /

After that you can run the UDF via the following SQL statement

.. code-block:: sql

    SELECT "<SCHEMA>"."<UDF_NAME>"('exa+bfs://...');
