.. _slct: https://exasol.github.io/script-languages-container-tool/main/index.html
.. _customize_slc:
   https://github.com/exasol/script-languages-release/blob/master/doc/user_guide/usage.md#how-to-customize-an-existing-flavor
.. _mlflow_extras_overview:
   https://github.com/mlflow/mlflow/blob/c9d7d067c1a2564b4380fc2d6c807518b8dcb179/EXTRA_DEPENDENCIES.rst
.. _mlflow_extra-ml-requirements:
   https://github.com/mlflow/mlflow/blob/master/requirements/extra-ml-requirements.txt
.. _mlflow_dependencies_general: https://mlflow.org/docs/latest/ml/model/dependencies/

Using a Script Language Container
=================================

Enabling a UDF to load MLflow models, requires the installation of the Exasol
MLflow Plugin incl. its dependencies into the Exasol Database.  This is done
by creating a dedicated `Script Language Container (SLC)
<https://github.com/exasol/script-languages-release>`_ for running the UDF.

Depending on the models you want to use in your UDF implementation, you might
need to add additional libraries as *dependencies* to be included in the SLC
image.

For details see

* `User Guide <customize_slc_>`_ of the ``script-languages-release`` repository
* Optional dependencies (aka. "extras") of MLflow: `Overview
  <mlflow_extras_overview_>`_
  and `Full Listing <mlflow_extra-ml-requirements_>`_
* MLflow documentation on `Dependencies in General <mlflow_dependencies_general_>`_

The SLC image then needs to be *deployed* to an Exasol database instance by
uploading it to the BucketFS and *activated* for the current active SQL
session or the system. For these steps, please see the `Exasol Script
Languages Container Tool User Guide <slct_>`_.
