Building the SLC Image
======================

The following command builds an SLC image containing the implementation of the
Exasol MLflow Plugin and all its dependencies and stores the image in
directory ``.slc``.

.. code-block:: shell

    poetry run nox -s slc:export
