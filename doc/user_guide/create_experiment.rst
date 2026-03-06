.. _create_mlflow_experiment:

Creating an MLflow Experiment
=============================

MLflow allows creating experiments via UI, CLI, and API.

.. _create_experiment_cli:
   https://mlflow.org/docs/latest/api_reference/cli.html#mlflow-experiments-create
.. _experiment_api:
   https://mlflow.org/docs/latest/ml/tracking/tracking-api/#experiment-organization


Via UI
------

Open the UI of your Mlflow server, click "Experiments" in the left hand menu,
and blue button "Create" on the upper right:

.. image:: create-experiment-ui.png
    :scale: 40 %
    :class: with-border


Via CLI
-------

.. code-block:: shell

    mlflow experiments create \
      --experiment-name "My Experiment" \
      --artifact-location "exa+bfs://localhost:2580/bfsdefault/default/"

For details, see `MLflow CLI Documentation <create_experiment_cli_>`_ and
:ref:`URI Format<uri_format>`.

Via API
-------

.. code-block:: python

    import mlflow

    uri = "exa+bfs://localhost:2580/bfsdefault/default/"
    mlflow.create_experiment("My Experiment", artifact_location=uri)
    mlflow.set_experiment("My Experiment")

For details, see the `MLflow API Documentation <experiment_api_>`_ and
:ref:`URI Format<uri_format>`.
