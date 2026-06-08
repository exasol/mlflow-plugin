.. _uri_format:

URI Format of Artifact URIs
===========================

The plugin requires that artifact URIs be specified in the following format:

.. code-block:: shell

    <scheme>://<host>:<port>/<bucketfs-service>/<bucket>/<path>

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Parameter
     - Description
   * - *<scheme>*
     - Either ``exa+bfs`` or ``exa+bfss`` for HTTP and HTTPS transfer,
       respectively.  Future releases of the plugin will also support ``exa+saas``
       for accessing the BucketFS of an Exasol SaaS instance.
   * - *<host>*
     - Name of the BucketFS service, e.g. ``localhost``.
   * - *<port>*
     - Port of the BucketFS service, e.g. ``2580``.
   * - *<bucketfs-service>*
     - Name of the BucketFS service, e.g. ``bfsdefault``.
   * - *<bucket>*
     - Name of the Bucket, e.g. ``default``.
   * - *<path>*
     - Optional sub-path within the bucket.

Environment Variables
---------------------

Additional parameters must be specified via environment variables:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Environment variable
     - Description
   * - ``EXA_BUCKETFS_PASSWORD``
     - Mandatory password.
   * - ``EXA_BUCKETFS_USER``
     - Optional username for writing to the BucketFS, defaults to ``w``.
   * - ``EXA_SSL_CERT_VALIDATION``
     - Optional setting, whether your client should
       verify the SSL certificates of the Exasol BucketFS service, either
       ``true`` or ``false``, defaults to ``true``.
