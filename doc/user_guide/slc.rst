.. _slct: https://exasol.github.io/script-languages-container-tool/main/index.html
.. _customize_slc: https://github.com/exasol/script-languages-release/blob/master/doc/user_guide/usage.md#how-to-customize-an-existing-flavor

Using a Script Language Container
=================================

Enabling a UDF to retrieve MLflow models, requires the implementation of the
Exasol MLflow Plugin incl. its dependencies to be available. This is done by
creating a dedicated `Script Language Container (SLC)
<https://github.com/exasol/script-languages-release>`_ for running the UDF.

Depending on the models you want to use in your UDF implementation, you might
need to add additional libraries as *dependencies* to be included in the SLC
image. For details see the `User Guide <customize_slc_>`_ of the
``script-languages-release`` repository.

The SLC image then needs to be *deployed* to an Exasol database instance by
uploading it to the BucketFS and *activated* for the current active SQL
session or the system. For these steps, please see the `Exasol Script
Languages Container Tool User Guide <slct_>`_.
