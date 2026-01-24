.. _user_guide:

:octicon:`person` User Guide
============================

This MLflow Plugin allows using the **Exasol Bucket File System** (BucketFS)
as MLflow Artifact Store. `BucketFS
<https://docs.exasol.com/db/latest/database_concepts/bucketfs/bucketfs.htm>`_
is a powerful feature for exchanging non-relational data with the database
nodes in an Exasol cluster.

* MLflow users can store and retrieve artifacts of AI models in the BucketFS
  of an Exasol database via the MLflow UI or its API.

* Applications and `User Defined Scripts
  <https://docs.exasol.com/db/latest/database_concepts/udf_scripts.htm>`_
  (UDFs) can retrieve models from Exasol BucketFS.

See the `MLflow documentation
<https://mlflow.org/docs/latest/self-hosting/architecture/artifact-store/#setting-a-default-artifact-location-for-logging>`_
for specifying the BucketFS Artifact Repository either when starting the
MLflow server or when creating an MLflow *experiment*.

The plugin requires artifact URIs to be specified in the following format:

.. code-block:: shell

    <scheme>://<host>:<port>/<bucketfs-service>/<bucket>/<path>

* ``<scheme>``: Either ``exa+bfs`` or ``exa+bfss`` for HTTP and HTTPS,
  respectively.  Future releases of the plugin will also support ``exa+saas``
  for accessing the BucketFS of an Exasol SaaS instance.
* ``<host>``: Name of the BucketFS service, e.g. ``localhost``.
* ``<port>``: Port of the BucketFS service, e.g. ``2580``.
* ``<bucketfs-service>``: Name of the BucketFS service, e.g. ``bfsdefault``.
* ``<bucket>``: Name of the Bucket, e.g. ``default``.
* ``<path>``: Optional sub-path within the bucket.

Additional parameters must be specified via environment variables:

* ``EXA_BUCKETFS_PASSWORD``: Mandatory password.
* ``EXA_BUCKETFS_USER``: Optional user name for writing to the BucketFS, defaults to ``w``.
* ``EXA_SSL_CERT_VALIDATION``: Optional setting, whether your client should
  verify the SSL certificates of the Exasol BucketFS service, either ``true``
  or ``false``, defaults to ``true``.

The following command line starts an MLflow server with the BucketFS as
default artifact store:

.. code-block:: shell

    EXA_BUCKETFS_PASSWORD="<your password>" \
    mlflow server --default-artifact-root \
    exa+bfs://localhost:2580/bfsdefault/default/

