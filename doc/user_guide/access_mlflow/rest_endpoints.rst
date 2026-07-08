UDF ``ARTIFACTS_LIST``
----------------------

Calls MLflow REST API endpoint `artifacts <https://mlflow.org/docs/latest/api_reference/rest-api.html#mlflowartifactsmlflowartifactsservicelistartifacts>`_.

.. code-block:: sql

    SELECT ARTIFACTS_LIST(
        connection_name, path
    );

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Input Column
     - SQL Type
     - Comment
   * - ``path``
     - ``VARCHAR(2000000)``
     - recommended


.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Output Column
     - SQL Type
   * - ``path``
     - ``VARCHAR(2000000)``
   * - ``is_dir``
     - ``BOOLEAN``
   * - ``file_size``
     - ``DECIMAL(18,0)``

UDF ``EXPERIMENTS_SEARCH``
--------------------------

Calls MLflow REST API endpoint `experiments/search <https://mlflow.org/docs/latest/api_reference/rest-api.html#search-experiments>`_.

.. code-block:: sql

    SELECT EXPERIMENTS_SEARCH(
        connection_name, filter, view_type, order_by, max_results
    );

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Input Column
     - SQL Type
     - Comment
   * - ``filter``
     - ``VARCHAR(2000000)``
     - 
   * - ``view_type``
     - ``VARCHAR(2000000)``
     - 
   * - ``order_by``
     - ``VARCHAR(2000000)``
     - 
   * - ``max_results``
     - ``DECIMAL(18,0)``
     - 


.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Output Column
     - SQL Type
   * - ``experiment_id``
     - ``VARCHAR(2000000)``
   * - ``name``
     - ``VARCHAR(2000000)``
   * - ``artifact_location``
     - ``VARCHAR(2000000)``
   * - ``lifecycle_stage``
     - ``VARCHAR(2000000)``
   * - ``updated``
     - ``TIMESTAMP(3)``
   * - ``created``
     - ``TIMESTAMP(3)``
   * - ``effective_trace_archival_retention``
     - ``VARCHAR(2000000)``
   * - ``tag_key``
     - ``VARCHAR(2000000)``
   * - ``tag_value``
     - ``VARCHAR(2000000)``

UDF ``GATEWAY_ENDPOINTS_LIST``
------------------------------

Calls MLflow REST API endpoint `gateway/endpoints/list <https://mlflow.org/docs/latest/api_reference/rest-api.html#list-gateway-endpoints>`_.

.. code-block:: sql

    SELECT GATEWAY_ENDPOINTS_LIST(
        connection_name, provider, secret_id
    );

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Input Column
     - SQL Type
     - Comment
   * - ``provider``
     - ``VARCHAR(2000000)``
     - 
   * - ``secret_id``
     - ``VARCHAR(2000000)``
     - 


.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Output Column
     - SQL Type
   * - ``endpoint_id``
     - ``VARCHAR(2000000)``
   * - ``name``
     - ``VARCHAR(2000000)``
   * - ``created_at``
     - ``TIMESTAMP(3)``
   * - ``last_updated_at``
     - ``TIMESTAMP(3)``
   * - ``created_by``
     - ``VARCHAR(2000000)``
   * - ``last_updated_by``
     - ``VARCHAR(2000000)``
   * - ``routing_strategy``
     - ``VARCHAR(2000000)``
   * - ``experiment_id``
     - ``VARCHAR(2000000)``
   * - ``usage_tracking``
     - ``BOOLEAN``
   * - ``fallback_strategy``
     - ``VARCHAR(2000000)``
   * - ``fallback_max_attempts``
     - ``DECIMAL(18,0)``
   * - ``tag_key``
     - ``VARCHAR(2000000)``
   * - ``tag_value``
     - ``VARCHAR(2000000)``

UDF ``GATEWAY_MODEL_DEFINITIONS_LIST``
--------------------------------------

Calls MLflow REST API endpoint `gateway/model-definitions/list <https://mlflow.org/docs/latest/api_reference/rest-api.html#list-gateway-model-definitions>`_.

.. code-block:: sql

    SELECT GATEWAY_MODEL_DEFINITIONS_LIST(
        connection_name, provider, secret_id
    );

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Input Column
     - SQL Type
     - Comment
   * - ``provider``
     - ``VARCHAR(2000000)``
     - 
   * - ``secret_id``
     - ``VARCHAR(2000000)``
     - 


.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Output Column
     - SQL Type
   * - ``model_definition_id``
     - ``VARCHAR(2000000)``
   * - ``name``
     - ``VARCHAR(2000000)``
   * - ``secret_id``
     - ``VARCHAR(2000000)``
   * - ``secret_name``
     - ``VARCHAR(2000000)``
   * - ``provider``
     - ``VARCHAR(2000000)``
   * - ``model_name``
     - ``VARCHAR(2000000)``
   * - ``created_at``
     - ``TIMESTAMP(3)``
   * - ``last_updated_at``
     - ``TIMESTAMP(3)``
   * - ``created_by``
     - ``VARCHAR(2000000)``
   * - ``last_updated_by``
     - ``VARCHAR(2000000)``
   * - ``fallback_strategy``
     - ``VARCHAR(2000000)``
   * - ``fallback_max_attempts``
     - ``DECIMAL(18,0)``
   * - ``tag_key``
     - ``VARCHAR(2000000)``
   * - ``tag_value``
     - ``VARCHAR(2000000)``

UDF ``MODEL_VERSIONS_GET``
--------------------------

Calls MLflow REST API endpoint `model-versions/get <https://mlflow.org/docs/latest/api_reference/rest-api.html#get-modelversion>`_.

.. code-block:: sql

    SELECT MODEL_VERSIONS_GET(
        connection_name, name, version
    );

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Input Column
     - SQL Type
     - Comment
   * - ``name``
     - ``VARCHAR(2000000)``
     - mandatory
   * - ``version``
     - ``VARCHAR(2000000)``
     - mandatory


.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Output Column
     - SQL Type
   * - ``name``
     - ``VARCHAR(2000000)``
   * - ``version``
     - ``VARCHAR(2000000)``
   * - ``created``
     - ``TIMESTAMP(3)``
   * - ``updated``
     - ``TIMESTAMP(3)``
   * - ``user_id``
     - ``VARCHAR(2000000)``
   * - ``current_stage``
     - ``VARCHAR(2000000)``
   * - ``description``
     - ``VARCHAR(2000000)``
   * - ``source``
     - ``VARCHAR(2000000)``
   * - ``run_id``
     - ``VARCHAR(2000000)``
   * - ``status``
     - ``VARCHAR(2000000)``
   * - ``status_message``
     - ``VARCHAR(2000000)``
   * - ``run_link``
     - ``VARCHAR(2000000)``
   * - ``aliases``
     - ``VARCHAR(2000000)``
   * - ``model_id``
     - ``VARCHAR(2000000)``
   * - ``tag_key``
     - ``VARCHAR(2000000)``
   * - ``tag_value``
     - ``VARCHAR(2000000)``

UDF ``MODEL_VERSIONS_GET_DOWNLOAD_URI``
---------------------------------------

Calls MLflow REST API endpoint `model-versions/get-download-uri <https://mlflow.org/docs/latest/api_reference/rest-api.html#get-download-uri-for-modelversion-artifacts>`_.

.. code-block:: sql

    SELECT MODEL_VERSIONS_GET_DOWNLOAD_URI(
        connection_name, name, version
    );

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Input Column
     - SQL Type
     - Comment
   * - ``name``
     - ``VARCHAR(2000000)``
     - mandatory
   * - ``version``
     - ``VARCHAR(2000000)``
     - mandatory


.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Output Column
     - SQL Type
   * - ``artifact_uri``
     - ``VARCHAR(2000000)``

UDF ``MODEL_VERSIONS_SEARCH``
-----------------------------

Calls MLflow REST API endpoint `model-versions/search <https://mlflow.org/docs/latest/api_reference/rest-api.html#search-modelversions>`_.

.. code-block:: sql

    SELECT MODEL_VERSIONS_SEARCH(
        connection_name, filter, order_by, max_results
    );

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Input Column
     - SQL Type
     - Comment
   * - ``filter``
     - ``VARCHAR(2000000)``
     - 
   * - ``order_by``
     - ``VARCHAR(2000000)``
     - 
   * - ``max_results``
     - ``DECIMAL(18,0)``
     - 


.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Output Column
     - SQL Type
   * - ``name``
     - ``VARCHAR(2000000)``
   * - ``version``
     - ``VARCHAR(2000000)``
   * - ``created``
     - ``TIMESTAMP(3)``
   * - ``updated``
     - ``TIMESTAMP(3)``
   * - ``user_id``
     - ``VARCHAR(2000000)``
   * - ``current_stage``
     - ``VARCHAR(2000000)``
   * - ``description``
     - ``VARCHAR(2000000)``
   * - ``source``
     - ``VARCHAR(2000000)``
   * - ``run_id``
     - ``VARCHAR(2000000)``
   * - ``status``
     - ``VARCHAR(2000000)``
   * - ``status_message``
     - ``VARCHAR(2000000)``
   * - ``run_link``
     - ``VARCHAR(2000000)``
   * - ``aliases``
     - ``VARCHAR(2000000)``
   * - ``model_id``
     - ``VARCHAR(2000000)``
   * - ``tag_key``
     - ``VARCHAR(2000000)``
   * - ``tag_value``
     - ``VARCHAR(2000000)``

UDF ``REGISTERED_MODEL_GET``
----------------------------

Calls MLflow REST API endpoint `registered-models/get <https://mlflow.org/docs/latest/api_reference/rest-api.html#get-registeredmodel>`_.

.. code-block:: sql

    SELECT REGISTERED_MODEL_GET(
        connection_name, name
    );

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Input Column
     - SQL Type
     - Comment
   * - ``name``
     - ``VARCHAR(2000000)``
     - mandatory


.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Output Column
     - SQL Type
   * - ``name``
     - ``VARCHAR(2000000)``
   * - ``created``
     - ``TIMESTAMP(3)``
   * - ``updated``
     - ``TIMESTAMP(3)``
   * - ``user_id``
     - ``VARCHAR(2000000)``
   * - ``description``
     - ``VARCHAR(2000000)``
   * - ``deployment_job_id``
     - ``VARCHAR(2000000)``
   * - ``deployment_job_state``
     - ``VARCHAR(2000000)``
   * - ``tag_key``
     - ``VARCHAR(2000000)``
   * - ``tag_value``
     - ``VARCHAR(2000000)``

UDF ``REGISTERED_MODELS_SEARCH``
--------------------------------

Calls MLflow REST API endpoint `registered-models/search <https://mlflow.org/docs/latest/api_reference/rest-api.html#search-registeredmodels>`_.

.. code-block:: sql

    SELECT REGISTERED_MODELS_SEARCH(
        connection_name, filter, order_by, max_results
    );

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Input Column
     - SQL Type
     - Comment
   * - ``filter``
     - ``VARCHAR(2000000)``
     - 
   * - ``order_by``
     - ``VARCHAR(2000000)``
     - 
   * - ``max_results``
     - ``DECIMAL(18,0)``
     - 


.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Output Column
     - SQL Type
   * - ``name``
     - ``VARCHAR(2000000)``
   * - ``created``
     - ``TIMESTAMP(3)``
   * - ``updated``
     - ``TIMESTAMP(3)``
   * - ``user_id``
     - ``VARCHAR(2000000)``
   * - ``description``
     - ``VARCHAR(2000000)``
   * - ``deployment_job_id``
     - ``VARCHAR(2000000)``
   * - ``deployment_job_state``
     - ``VARCHAR(2000000)``
   * - ``tag_key``
     - ``VARCHAR(2000000)``
   * - ``tag_value``
     - ``VARCHAR(2000000)``

UDF ``REGISTERED_MODELS_GET_LATEST_VERSIONS``
---------------------------------------------

Calls MLflow REST API endpoint `registered-models/get-latest-versions <https://mlflow.org/docs/latest/api_reference/rest-api.html#get-latest-modelversions>`_.

.. code-block:: sql

    SELECT REGISTERED_MODELS_GET_LATEST_VERSIONS(
        connection_name, name, stages
    );

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Input Column
     - SQL Type
     - Comment
   * - ``name``
     - ``VARCHAR(2000000)``
     - mandatory
   * - ``stages``
     - ``VARCHAR(2000000)``
     - 


.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Output Column
     - SQL Type
   * - ``name``
     - ``VARCHAR(2000000)``
   * - ``version``
     - ``VARCHAR(2000000)``
   * - ``created``
     - ``TIMESTAMP(3)``
   * - ``updated``
     - ``TIMESTAMP(3)``
   * - ``user_id``
     - ``VARCHAR(2000000)``
   * - ``current_stage``
     - ``VARCHAR(2000000)``
   * - ``description``
     - ``VARCHAR(2000000)``
   * - ``source``
     - ``VARCHAR(2000000)``
   * - ``run_id``
     - ``VARCHAR(2000000)``
   * - ``status``
     - ``VARCHAR(2000000)``
   * - ``status_message``
     - ``VARCHAR(2000000)``
   * - ``run_link``
     - ``VARCHAR(2000000)``
   * - ``aliases``
     - ``VARCHAR(2000000)``
   * - ``model_id``
     - ``VARCHAR(2000000)``
   * - ``tag_key``
     - ``VARCHAR(2000000)``
   * - ``tag_value``
     - ``VARCHAR(2000000)``

UDF ``RUNS_SEARCH``
-------------------

Calls MLflow REST API endpoint `runs/search <https://mlflow.org/docs/latest/api_reference/rest-api.html#search-runs>`_.

.. code-block:: sql

    SELECT RUNS_SEARCH(
        connection_name, experiment_ids, filter, run_view_type, order_by, max_results
    );

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Input Column
     - SQL Type
     - Comment
   * - ``experiment_ids``
     - ``VARCHAR(2000000)``
     - recommended
   * - ``filter``
     - ``VARCHAR(2000000)``
     - 
   * - ``run_view_type``
     - ``VARCHAR(2000000)``
     - 
   * - ``order_by``
     - ``VARCHAR(2000000)``
     - 
   * - ``max_results``
     - ``DECIMAL(18,0)``
     - 


.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Output Column
     - SQL Type
   * - ``run_id``
     - ``VARCHAR(2000000)``
   * - ``run_uuid``
     - ``VARCHAR(2000000)``
   * - ``run_name``
     - ``VARCHAR(2000000)``
   * - ``experiment_id``
     - ``VARCHAR(2000000)``
   * - ``user_id``
     - ``VARCHAR(2000000)``
   * - ``status``
     - ``VARCHAR(2000000)``
   * - ``start_time``
     - ``TIMESTAMP(3)``
   * - ``end_time``
     - ``TIMESTAMP(3)``
   * - ``artifact_uri``
     - ``VARCHAR(2000000)``
   * - ``lifecycle_stage``
     - ``VARCHAR(2000000)``
   * - ``tag_key``
     - ``VARCHAR(2000000)``
   * - ``tag_value``
     - ``VARCHAR(2000000)``

