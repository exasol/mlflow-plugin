Building the SLC Image
======================

The following command builds an SLC image containing the implementation of the
Exasol MLflow Plugin and all its dependencies and stores the image in
the directory ``.slc``.

.. code-block:: shell

    poetry run nox -s slc:export


Deploying the SLC and Activating the Script Language
----------------------------------------------------

You can use ``curl`` and follow the instructions on `docs.exasol.com
<https://docs.exasol.com/db/latest/database_concepts/udf_scripts/adding_new_packages_script_languages.htm#UseaprebuiltscriptlanguagecontainerSLC>`_
for uploading the SLC to the BucketFS and activating the script language with
a language alias.

However, it is much simpler to run an :ref:`integration test
<slc_interaction>`. You can check the activated scripts in system table
`EXA_PARAMETERS <https://docs.exasol.com/db/latest/sql/alter_session.htm>`_:

.. code-block:: sql

    SELECT * from EXA_PARAMETERS WHERE PARAMETER_NAME = 'SCRIPT_LANGUAGES';
