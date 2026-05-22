Building the SLC Image
======================

The following command builds an SLC image containing the implementation of the
Exasol MLflow Plugin and all its dependencies and stores the image in
directory ``.slc``.

.. code-block:: shell

    poetry run nox -s slc:export


Deploying the SLC
-----------------

For upload you can use ``curl``:

.. code-block:: shell

    FILE=.slc/*.tar.gz
    curl -v --insecure -T "$FILE" "https://localhost:2581/$(basename $FILE)"

The specified port needs to be forwarded by the Docker container.

If using http, then the port might be ``2580``, and ``curl`` option ``--insecure`` is not required:

.. code-block:: shell

    curl -v -T "$FILE" "http://localhost:2580/$(basename $FILE)"

Activating the Script Language
------------------------------

For activation, please note

* The SLC is named ``exasol_mlflow_plugin_release.tar.gz``
* Hence the activation will contain ``exasol_mlflow_plugin_release``
* The Path in the BucketFS is probably ``/bfsdefault/default``
* See also `docs.exasol.com <https://docs.exasol.com/db/latest/database_concepts/udf_scripts/adding_new_packages_script_languages.htm#UseaprebuiltscriptlanguagecontainerSLC>`_

You can use the following Nox session to display the actvation command:

.. code-block:: shell

    poetry run nox -s slc:activation

You can check the current value in system table `EXA_PARAMETERS <https://docs.exasol.com/db/latest/sql/alter_session.htm>`_:

.. code-block:: sql

    SELECT * from EXA_PARAMETERS WHERE PARAMETER_NAME = 'SCRIPT_LANGUAGES';
