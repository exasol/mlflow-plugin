Alternatives for Loading an MLflow Model
----------------------------------------

The following figure shows different alternatives for loading an MLflow model
from within a UDF:

.. image:: udf-loading-alternatives.svg
    :scale: 100 %

See the differences, prerequisites, benefits and drawbacks compared in the
following table:

.. list-table::
   :header-rows: 1

   * -
     - From the Local File System
     - Via MLflow REST API
   * - Speed
     - **Fastest option**
     - Significantly slower
   * - Supported Artifact Stores
     - Only BucketFS
     - Arbitrary, incl. BucketFS
   * - Setting the MLflow Tracking URI
     - Not required
     - Required

When you cannot guarantee the model to be accessible in the local file system
of the UDF, some **utility functions** will help you to automatically choose
the fastest loading option. See the examples in the following sections for
details.

MLflow Tracking URI
-------------------

In all cases where the UDF may access the MLflow server, it needs to set the
MLflow Tracking URI. This can be done by:

* Setting the environment variable ``MLFLOW_TRACKING_URI`` or
* Calling ``mlflow.set_tracking_uri()`` within the UDF implementation.

Depending on the environment your Exasol instance is running in, the
MLflow Tracking URI might differ from the one you can use on your local
machine. This applies in particular when running an `Exasol DockerDB
<exasol_docker_db_>`_ instance inside a virtual machine.

.. _exasol_docker_db: https://github.com/exasol/docker-db
