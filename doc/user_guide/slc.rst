Building and Deploying the Script Language Container
====================================================

..
  The project description of the Exasol MLflow Plugin defines the following dependencies:

  * The implementation of the plugin itself
  * Exasol BucketFS Client
  * The MLflow Client API

Enabling a UDF to retrieve MLflow models, requires the implementation of the
Exasol MLflow Plugin incl. its dependencies to be available.  This is done by
creating a dedicated `Script Language Container (SLC)
<https://github.com/exasol/script-languages-release>`_ for running the UDF.

The current section guides you to build, the SLC, upload it to Exasol's
BucketFS and activate it for running UDFs.

Building the SLC
----------------

The following command offered by Exasol MLflow Plugin builds an SLC image
containing the implementation of the Exasol MLflow Plugin and all its
dependencies and stores the image in directory ``.slc``.

.. code-block:: shell

    poetry run nox -s slc:export

Deploying the SLC
-----------------

An SLC image can be deployed to an Exasol database instance by uploading it to
the BucketFS.

t.b.d.

Activating the SLC
------------------

Before running a UDF in an SLC, the SLC image needs to be deployed and
*activated* for the current active SQL session or the system, the latter
requiring administration permissions.

t.b.d.
