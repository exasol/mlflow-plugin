.. _install_slc:

Using a Script Language Container
=================================

Loading MLflow models in a UDF or using the REST API UDFs requires the installation of the Exasol MLflow
Plugin and its dependencies into the Exasol Database.  This is done by
creating a dedicated `Script Language Container (SLC)
<https://github.com/exasol/script-languages-release>`_ for running the UDF.

Depending on the models you want to use in your UDF implementation, you might
need to add additional libraries as *dependencies* to be included in the
SLC. See also

* The MLflow documentation on `dependencies in general
  <mlflow_dependencies_general_>`_
* An overview of `MLflow optional dependencies
  <mlflow_extras_overview_>`_ (aka. "Extras")
* The entire `list of MLflow extras <mlflow_extra-ml-requirements_>`_

``ALTER SESSION`` or ``ALTER SYSTEM`` Statement
-----------------------------------------------

For general information on SLCs, incl.  deployment (upload to Exasol's Bucket
File System) and activation, see the documentation at `docs.exasol.com
<slcs_>`_.

When activating the Exasol's MLflow SLC, the language is ``python`` and the
language alias must be ``EXA_MLFLOW``.

.. code-block:: sql

    EXA_MLFLOW=localzmq+protobuf:///<bucketfs_name>/<bucket_name>/<path_in_bucket>/<container_name>/?lang=python#buckets/<bucketfs_name>/<bucket_name>/<path_in_bucket>/<container_name>/exaudf/exaudfclient

.. _mlflow_dependencies_general: https://mlflow.org/docs/latest/ml/model/dependencies/
.. _mlflow_extras_overview:
   https://github.com/mlflow/mlflow/blob/c9d7d067c1a2564b4380fc2d6c807518b8dcb179/EXTRA_DEPENDENCIES.rst
.. _mlflow_extra-ml-requirements:
   https://github.com/mlflow/mlflow/blob/master/requirements/extra-ml-requirements.txt
.. _slcs: https://docs.exasol.com/db/latest/database_concepts/udf_scripts/adding_new_packages_script_languages.htm
