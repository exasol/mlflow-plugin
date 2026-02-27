Accessing Artifacts from Within a UDF
=====================================

Using the Exasol MLflow Plugin significantly speeds up loading MLflow models
in Exasol `UDFs
<https://docs.exasol.com/db/latest/database_concepts/udf_scripts.htm>`_.

After having built, deployed, and activated your SLC, you can use Exasol SQL
to define a UDF like this:

.. code-block:: sql

    --/
    CREATE OR REPLACE MLFLOW_SLC
       SCALAR SCRIPT "<SCHEMA>"."<UDF_NAME>"(uri VARCHAR(2000))
       RETURNS BOOL AS
    import mlflow
    from exasol.mlflow_plugin.artifacts.bucketfs_connector import udf_path
    def run(ctx):
        path = udf_path(ctx.uri)
        model = mlflow.sklearn.load_model(path)
        #--
        #-- your implementation using the model goes here
        #--
        return True
    /

Now you can run the UDF via the following SQL statement

.. code-block:: sql

    SELECT "<SCHEMA>"."<UDF_NAME>"('exa+bfs://...');
