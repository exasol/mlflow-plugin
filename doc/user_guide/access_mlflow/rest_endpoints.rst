UDF ``EXPERIMENTS_SEARCH``
--------------------------

Calls MLflow REST API endpoint `experiments/search <https://mlflow.org/docs/latest/api_reference/rest-api.html#search-experiments>`_.

Sample Call
^^^^^^^^^^^

.. code-block:: sql

    SELECT EXPERIMENTS_SEARCH(
        connection_name, filter, view_type, order_by, max_results
    );

Input Columns
^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 30 50

   * - Name
     - SQL Type
   * - ``filter``
     - ``VARCHAR(2000000)``
   * - ``view_type``
     - ``VARCHAR(2000000)``
   * - ``order_by``
     - ``VARCHAR(2000000)``
   * - ``max_results``
     - ``DECIMAL(18,0)``

Output Columns
^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 30 50

   * - Name
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
