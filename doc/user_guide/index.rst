.. _user_guide:

:octicon:`person` User Guide
============================

This MLflow Plugin allows using the **Exasol Bucket File System** (BucketFS)
as an *MLflow Artifact Store*.

`BucketFS
<https://docs.exasol.com/db/latest/database_concepts/bucketfs/bucketfs.htm>`_
is a powerful feature for exchanging non-relational data with the database
nodes in an Exasol cluster.

* MLflow users can store and retrieve artifacts of AI models in the BucketFS
  of an Exasol database via the MLflow UI or its APIs.

* Applications and `User Defined Scripts
  <https://docs.exasol.com/db/latest/database_concepts/udf_scripts.htm>`_
  (UDFs) can retrieve models from Exasol BucketFS very fast.  Loading a 600 MB
  Huggingface model from BucketFS can take less than 2% of the time compared
  to MLflow's regular HTTP interface.

Contents
--------

.. toctree::
   :maxdepth: 1

   installation
   mlflow_server
   create_experiment
   uri_format
   plugin_availability
   slc
   udfs
