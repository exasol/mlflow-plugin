.. _starting the MLflow server:

Using the BucketFS Artifact Store
=================================

See the `MLflow documentation
<https://mlflow.org/docs/latest/self-hosting/architecture/artifact-store/#setting-a-default-artifact-location-for-logging>`_
for specifying the BucketFS Artifact Store either when starting the MLflow
server or when creating an MLflow *experiment*.

.. image:: enabling-bucketfs-artifact-store.svg
    :scale: 130 %


As Default Artifact Repository
------------------------------

The following command line starts an MLflow server with the BucketFS as the
default artifact store:

.. code-block:: shell

    EXA_BUCKETFS_PASSWORD="<your password>" \
    mlflow server --default-artifact-root \
    exa+bfs://localhost:2580/bfsdefault/default/

This option is only available if you have access to the MLflow server and can
change its startup options.

For more details, see :ref:`uri_format`.

In the Scope of an Individual MLflow Experiment
-----------------------------------------------

.. _set_experiment:
   https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.set_experiment

If you cannot change the startup options of your MLflow server, then you still
can use the BucketFS Artifact Store for individual MLflow *experiments*.

:ref:`create_mlflow_experiment` describes how to create an MLflow experiment
via UI, CLI, and API.

As soon as such an experiment exists, you can use it via MLflow API function
``set_experiment()`` providing the name or the ID of the experiment as
argument.

.. code-block:: python

    import mlflow
    import sklearn

    mlflow.set_experiment("My Experiment")
    model = sklearn.linear_model.LogisticRegression()
    info = mlflow.sklearn.log_model(model, name="My_Model")
    print(f"stored model at {info.artifact_path}")


For details, see the `MLflow API function set_experiment()
<set_experiment_>`_.
