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
    %env MLFLOW_TRACKING_URI=http://localhost:5000
    import mlflow
    from exasol.mlflow_plugin.artifacts.bucketfs_connector import (
        local_path_or_uri
    )
    def run(ctx):
        locator = local_path_or_uri(ctx.uri)
        model = mlflow.sklearn.load_model(locator)
        #--
        #-- your implementation using the model goes here
        #--
        return True
    /

Now you can run the UDF via the following SQL statement

.. code-block:: sql

    SELECT "<SCHEMA>"."<UDF_NAME>"('exa+bfs://...');

.. note::

   The function ``local_path_or_uri()`` checks if

   * The URI points to the BucketFS artifact store and
   * The associated path is mounted into the local file system of the UDF.

   If any of these preconditions is false, then the ``locator`` will remain
   identical to the URI and hence load the model via the ordinary MLflow
   interface including network data transfer which can be significantly slower
   compared to loading a model directly from the BucketFS.

Another option is using ``load_model_with_fallback()``:

.. code-block:: sql

    --/
    CREATE OR REPLACE MLFLOW_SLC
       SCALAR SCRIPT "<SCHEMA>"."<UDF_NAME>"(uri VARCHAR(2000))
       RETURNS BOOL AS
    import mlflow
    from exasol.mlflow_plugin.artifacts.bucketfs_connector import (
        load_model_with_fallback
    )
    def run(ctx):
        mlflow.set_tracking_uri("http://localhost:5000")
        model = load_model_with_fallback(ctx.uri, mlflow.sklearn.load_model)
        return True
    /
