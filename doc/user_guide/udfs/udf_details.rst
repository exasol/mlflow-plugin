Creating and Running UDFs
-------------------------

Creating the UDF
++++++++++++++++

After having built, deployed, and activated your SLC, you can use Exasol SQL
to define a UDF like this:

.. literalinclude:: ../../../test/integration/with_mlflow_server/test_udfs.py
  :caption: Sample UDF loading an MLflow model using function
            ``local_path_or_uri()`` to read the model from the local file
            system if possible. The MLflow Tracking URI is passed via
            environment variable ``MLFLOW_TRACKING_URI``.
  :language: python
  :start-after: User Guide sample UDF #1
  :end-before: /end-sample
  :dedent: 8


Running the UDF
+++++++++++++++

Now you can run the UDF via the following SQL statement

.. code-block:: sql

    SELECT "<SCHEMA>"."<UDF_NAME>"('exa+bfs://...');

Function ``local_path_or_uri()``
++++++++++++++++++++++++++++++++

The function checks if:

* The URI points to the BucketFS artifact store and
* The associated path is mounted into the local file system of the UDF.

If both conditions are true, then the function will return a path in the local
file system, that can be passed to one of the ``load_model()`` functions of
the MLflow API, e.g. ``mlflow.models.Model.load()`` or
``mlflow.sklearn.load_model()``.

Otherwise the function will return the original URI without changes, for
loading the model via the MLflow server which can be significantly slower.

Function ``load_model_with_fallback()``
+++++++++++++++++++++++++++++++++++++++

Another option is using this function, which accepts the URI and the actual
load-function as arguments.

.. literalinclude:: ../../../test/integration/with_mlflow_server/test_udfs.py
  :caption: Sample UDF loading an MLflow model via
            ``load_model_with_fallback()``. The MLflow Tracking URI is set via
            ``mlflow.set_tracking_uri()`` within the implementation of the
            UDF.
  :language: python
  :start-after: User Guide sample UDF #2
  :end-before: /end-sample
  :dedent: 8
