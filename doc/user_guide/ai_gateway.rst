Accessing MLflow AI Gateways
============================

The following figure shows the basic system setup for accessing an MLflow AI
Gateway from within a UDF:

.. image:: img/ai-gateway/system-setup.svg
    :scale: 140 %

In order to use such a setup, you need to

* Have access to an external Model Inference service or start it locally (e.g. `Ollama <ollama_>`_).
* Have a model inside the inference service.
* Create an AI Gateway endpoint in MLflow, see `MLflow documentation <create_endpoint_>`_.

.. _ollama: https://github.com/ollama/ollama/
.. _create_endpoint:
   https://mlflow.org/docs/latest/genai/governance/ai-gateway/endpoints/create-and-manage

.. _access_ai_gateway:

Accessing an AI Gateway From Python
-----------------------------------

The MLflow documentation on `MLflow Invocations API
<mlflow-invocations-api_>`_ contains examples for cURL and Python, while the
Python example actually only uses the REST API via python library `requests
<requests_>`_.

.. code-block:: python

    import requests

    def send_request_to_ai_gateway(
        endpoint: str,
        mlflow_tracking_uri: str = "http://localhost:5000",
        auth: tuple[str, str] | None = None,
        question: str = "",
    ) -> dict:
        url = f"{mlflow_tracking_uri}/gateway/{endpoint}/mlflow/invocations"
        jreq = {
            "messages": [{ "role": "user", "content": question}],
            "max_tokens": 400,
            "temperature": 0.7,
        }
        response = requests.post(url, json=jreq, auth=auth)
        return response.json()

.. _mlflow-invocations-api:
   https://mlflow.org/docs/latest/genai/governance/ai-gateway/endpoints/query-endpoints/#mlflow-invocations-api
.. _requests: https://pypi.org/project/requests/

Accessing an AI Gateway From Within a UDF
-----------------------------------------

Creating an Exasol Connection
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For accessing an MLflow AI Gateway endpoint from within a UDF you should store
the MLflow tracking URI in an `Exasol Connection <exa_connection_>`_. The
Connection can also hold the authentication credentials for the MLflow server
which is usually required and recommended for production setups.

Here is an example for creating such a *Connection* for a basic authentication
with user name and password, see the `MLflow documentation <mlflow_auth_>`_
for other authentication variants.

.. code-block:: SQL

    CREATE OR REPLACE CONNECTION "MLFLOW"
        TO '<mlflow_tracking_uri>'
        USER '<user_name>'
        IDENTIFIED BY '<password>';

.. _exa_connection: https://docs.exasol.com/db/latest/sql/create_connection.htm
.. _mlflow_auth:
   https://mlflow.org/docs/latest/self-hosting/security/basic-http-auth/#using-rest-api

UDF Content
^^^^^^^^^^^

A UDF can securely read the MLflow tracking URI and the authentication secrets
from the connection object and call the function
``send_request_to_ai_gateway()`` defined :ref:`above <access_ai_gateway>`:

.. code-block:: sql

    --/
    CREATE OR REPLACE PYTHON3 SCALAR SCRIPT ASK_AI (
        endpoint VARCHAR(2000000),
        question VARCHAR(2000000)
    )
    EMITS (
        answer VARCHAR(2000000)
    ) AS

    # Add function send_request_to_ai_gateway() here!

    def run(ctx):
        conn = exa.get_connection("MLFLOW")
        resp = send_request_to_ai_gateway(
            ctx.endpoint,
            conn.address,
            auth=(conn.user, conn.password),
            question=ctx.question,
        )
        try:
            answer = resp["choices"][0]["message"]["content"]
        except:
            answer = ""
        ctx.emit(answer)
    /
    ;

    SELECT ASK_AI('What is the capital of Germany? (Keep it short)');


For more details please see Exasol's documentation on `Python UDFs
<python_udfs_>`_ and `UDFs in general <udfs_>`_.

.. _udfs:
   https://docs.exasol.com/db/latest/database_concepts/udf_scripts.htm
.. _python_udfs:
   https://docs.exasol.com/db/latest/database_concepts/udf_scripts/python3.htm
