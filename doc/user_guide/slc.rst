
.. _mlflow_dependencies_general: https://mlflow.org/docs/latest/ml/model/dependencies/
.. _mlflow_extras_overview:
   https://github.com/mlflow/mlflow/blob/c9d7d067c1a2564b4380fc2d6c807518b8dcb179/EXTRA_DEPENDENCIES.rst
.. _mlflow_extra-ml-requirements:
   https://github.com/mlflow/mlflow/blob/master/requirements/extra-ml-requirements.txt


.. _slcs: https://github.com/exasol/script-languages-release/blob/master/doc/user_guide/usage.md
.. _customize_slc:
   https://github.com/exasol/script-languages-release/blob/master/doc/user_guide/usage.md#how-to-customize-an-existing-flavor
.. _export_slc:
   https://github.com/exasol/script-languages-release/blob/master/doc/user_guide/usage.md#export-a-flavor
.. _activate-slc:
   https://github.com/exasol/script-languages-release/blob/master/doc/user_guide/usage.md#how-to-activate-a-script-language-container-in-the-database

Using a Script Language Container
=================================

Enabling a UDF to load MLflow models, requires the installation of the Exasol
MLflow Plugin incl. its dependencies into the Exasol Database.  This is done
by creating a dedicated `Script Language Container (SLC)
<https://github.com/exasol/script-languages-release>`_ for running the UDF.

Depending on the models you want to use in your UDF implementation, you might
need to add additional libraries as *dependencies* to be included in the
SLC. See also

* The MLflow documentation on `dependencies in general
  <mlflow_dependencies_general_>`_
* An overview about `MLflow optional dependencies
  <mlflow_extras_overview_>`_ (aka. "Extras")
* The entire `list of MLflow extras <mlflow_extra-ml-requirements_>`_

For more information on SLCs, see the `User Guide <slcs_>`_ of the
``script-languages-release`` repository incl. `customizing <customize_slc_>`_,
`deploying <export_slc_>`_, and `activating <activate-slc_>`_ SLCs.


