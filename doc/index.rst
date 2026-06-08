Exasol MLflow Plugin
====================

The Exasol MLflow Plugin supports using the open source AI engineering
platform `MLFlow <https://mlflow.org>`_ with Exasol.

This plugin enables using the Exasol BucketFS as *MLflow Artifact Store* and
accessing the MLflow REST API from Exasol.

* Remove section
Creating an MLflow Experiment

New structure

* Installation
  * Installing the Plugin
  * Using a Script Language Container
* Accessing the MLflow Server
  * REST API (planned)
  * Virtual Schema
* Accessing MLflow Models from UDFs
  Split into (1) intro and (2) details (= UDFs)
  * Using the BucketFS Artifact Store
    * Store MLFlow Experiment Artifacts in BucketFs
      (formerly named "Creating an..")
    * URI Format
    * When and for Which Operations is the MLflow Plugin Required?
  * UDF details (split from above)
* Accessing MLflow AI Gateways




Bucket FS Feature / User Guide
* URI Format of Artifact URIs
* Accessing Artifacts from Within a UDF

~/doc/AI/MLflow/P3-AI-Gateway/Grafik-Torsten.drawio


Accessing MLflow models
* BucketFS

Accessing the MLflow Backend Store Via an Exasol Virtual Schema


.. grid:: 1 1 3 2
    :gutter: 2
    :padding: 0
    :class-container: surface

    .. grid-item-card:: :octicon:`rocket` Features
        :link: features
        :link-type: ref

        Features of this plugin

    .. grid-item-card:: :octicon:`person` User Guide
        :link: user_guide
        :link-type: ref

        Resource for users to understand how to utilize this project and its features.

    .. grid-item-card:: :octicon:`tools` Developer Guide
        :link: developer_guide
        :link-type: ref

        Instructions and best practices to help developers contributing to the project and setting up their development environment.

    .. grid-item-card:: :octicon:`question` FAQ
        :link: faq
        :link-type: ref

        Frequently asked questions.

.. toctree::
   :maxdepth: 1
   :hidden:

   features/index
   user_guide/index
   developer_guide/index
   api
   faq
   changes/changelog
