.. _starting the MLflow server:

Using the BucketFS Artifact Store
=================================

See the `MLflow documentation
<https://mlflow.org/docs/latest/self-hosting/architecture/artifact-store/#setting-a-default-artifact-location-for-logging>`_
for specifying the BucketFS Artifact Store either when starting the MLflow
server or when creating an MLflow *experiment*.

The following command line starts an MLflow server with the BucketFS as the
default artifact store:

.. code-block:: shell

    EXA_BUCKETFS_PASSWORD="<your password>" \
    mlflow server --default-artifact-root \
    exa+bfs://localhost:2580/bfsdefault/default/

For more details, see :ref:`uri_format`.
