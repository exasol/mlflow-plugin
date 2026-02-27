.. _slct: https://exasol.github.io/script-languages-container-tool/main/index.html
.. _customize_slc: https://github.com/exasol/script-languages-release/blob/master/doc/user_guide/usage.md#how-to-customize-an-existing-flavor

Building and Deploying the Script Language Container
====================================================

..
  The project description of the Exasol MLflow Plugin defines the following dependencies:

  * The implementation of the plugin itself
  * Exasol BucketFS Client
  * The MLflow Client API

Enabling a UDF to retrieve MLflow models, requires the implementation of the
Exasol MLflow Plugin incl. its dependencies to be available. This is done by
creating a dedicated `Script Language Container (SLC)
<https://github.com/exasol/script-languages-release>`_ for running the UDF.

The current section guides you to build, the SLC, upload it to Exasol's
BucketFS and activate it for running UDFs.

Adding Additional Dependencies
------------------------------

Depending on the AI models you want to use in your UDF implementation, you
might need to add additional libraries as dependencies to be included in the
SLC image.

Please see the `instructions for customizing an SLC flavor <customize_slc_>`_.

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

See `Exasol Script Languages Container Tool User Guide <slct_>`_ for details.

Activating the SLC
------------------

Before running a UDF in a SLC, the SLC image needs to be deployed and
*activated* for the current active SQL session or the system, the latter
requiring administration permissions.

See `Exasol Script Languages Container Tool User Guide <slct_>`_ for details.
