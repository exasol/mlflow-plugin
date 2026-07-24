--/
CREATE OR REPLACE MLFLOW SCALAR SCRIPT "ARTIFACTS_LIST" (
  "connection_name" VARCHAR(2000000),
  "path" VARCHAR(2000000)
) EMITS (
  "path" VARCHAR(2000000),
  "is_dir" BOOLEAN,
  "file_size" DECIMAL(18,0)
) AS
from exasol.mlflow_plugin import rest_api

udf_call = rest_api.UdfCall(exa, endpoint=rest_api.ARTIFACTS_LIST)

def run(ctx):
    udf_call.run(ctx)
/ 

--/
CREATE OR REPLACE MLFLOW SCALAR SCRIPT "EXPERIMENTS_SEARCH" (
  "connection_name" VARCHAR(2000000),
  "filter" VARCHAR(2000000),
  "view_type" VARCHAR(2000000),
  "order_by" VARCHAR(2000000),
  "max_results" DECIMAL(18,0)
) EMITS (
  "experiment_id" VARCHAR(2000000),
  "name" VARCHAR(2000000),
  "artifact_location" VARCHAR(2000000),
  "lifecycle_stage" VARCHAR(2000000),
  "updated" TIMESTAMP(3),
  "created" TIMESTAMP(3),
  "effective_trace_archival_retention" VARCHAR(2000000),
  "tag_key" VARCHAR(2000000),
  "tag_value" VARCHAR(2000000)
) AS
from exasol.mlflow_plugin import rest_api

udf_call = rest_api.UdfCall(exa, endpoint=rest_api.EXPERIMENTS_SEARCH)

def run(ctx):
    udf_call.run(ctx)
/ 

--/
CREATE OR REPLACE MLFLOW SCALAR SCRIPT "GATEWAY_ENDPOINTS_LIST" (
  "connection_name" VARCHAR(2000000),
  "provider" VARCHAR(2000000),
  "secret_id" VARCHAR(2000000)
) EMITS (
  "endpoint_id" VARCHAR(2000000),
  "name" VARCHAR(2000000),
  "created_at" TIMESTAMP(3),
  "last_updated_at" TIMESTAMP(3),
  "created_by" VARCHAR(2000000),
  "last_updated_by" VARCHAR(2000000),
  "routing_strategy" VARCHAR(2000000),
  "experiment_id" VARCHAR(2000000),
  "usage_tracking" BOOLEAN,
  "fallback_strategy" VARCHAR(2000000),
  "fallback_max_attempts" DECIMAL(18,0),
  "tag_key" VARCHAR(2000000),
  "tag_value" VARCHAR(2000000)
) AS
from exasol.mlflow_plugin import rest_api

udf_call = rest_api.UdfCall(exa, endpoint=rest_api.GATEWAY_ENDPOINTS_LIST)

def run(ctx):
    udf_call.run(ctx)
/ 

--/
CREATE OR REPLACE MLFLOW SCALAR SCRIPT "GATEWAY_MODEL_DEFINITIONS_LIST" (
  "connection_name" VARCHAR(2000000),
  "provider" VARCHAR(2000000),
  "secret_id" VARCHAR(2000000)
) EMITS (
  "model_definition_id" VARCHAR(2000000),
  "name" VARCHAR(2000000),
  "secret_id" VARCHAR(2000000),
  "secret_name" VARCHAR(2000000),
  "provider" VARCHAR(2000000),
  "model_name" VARCHAR(2000000),
  "created_at" TIMESTAMP(3),
  "last_updated_at" TIMESTAMP(3),
  "created_by" VARCHAR(2000000),
  "last_updated_by" VARCHAR(2000000),
  "fallback_strategy" VARCHAR(2000000),
  "fallback_max_attempts" DECIMAL(18,0),
  "tag_key" VARCHAR(2000000),
  "tag_value" VARCHAR(2000000)
) AS
from exasol.mlflow_plugin import rest_api

udf_call = rest_api.UdfCall(exa, endpoint=rest_api.GATEWAY_MODEL_DEFINITIONS_LIST)

def run(ctx):
    udf_call.run(ctx)
/ 

--/
CREATE OR REPLACE MLFLOW SCALAR SCRIPT "MODEL_VERSIONS_GET" (
  "connection_name" VARCHAR(2000000),
  "name" VARCHAR(2000000),
  "version" VARCHAR(2000000)
) EMITS (
  "name" VARCHAR(2000000),
  "version" VARCHAR(2000000),
  "created" TIMESTAMP(3),
  "updated" TIMESTAMP(3),
  "user_id" VARCHAR(2000000),
  "current_stage" VARCHAR(2000000),
  "description" VARCHAR(2000000),
  "source" VARCHAR(2000000),
  "run_id" VARCHAR(2000000),
  "status" VARCHAR(2000000),
  "status_message" VARCHAR(2000000),
  "run_link" VARCHAR(2000000),
  "aliases" VARCHAR(2000000),
  "model_id" VARCHAR(2000000),
  "tag_key" VARCHAR(2000000),
  "tag_value" VARCHAR(2000000)
) AS
from exasol.mlflow_plugin import rest_api

udf_call = rest_api.UdfCall(exa, endpoint=rest_api.MODEL_VERSIONS_GET)

def run(ctx):
    udf_call.run(ctx)
/ 

--/
CREATE OR REPLACE MLFLOW SCALAR SCRIPT "MODEL_VERSIONS_GET_DOWNLOAD_URI" (
  "connection_name" VARCHAR(2000000),
  "name" VARCHAR(2000000),
  "version" VARCHAR(2000000)
) EMITS (
  "artifact_uri" VARCHAR(2000000)
) AS
from exasol.mlflow_plugin import rest_api

udf_call = rest_api.UdfCall(exa, endpoint=rest_api.MODEL_VERSIONS_GET_DOWNLOAD_URI)

def run(ctx):
    udf_call.run(ctx)
/ 

--/
CREATE OR REPLACE MLFLOW SCALAR SCRIPT "MODEL_VERSIONS_SEARCH" (
  "connection_name" VARCHAR(2000000),
  "filter" VARCHAR(2000000),
  "order_by" VARCHAR(2000000),
  "max_results" DECIMAL(18,0)
) EMITS (
  "name" VARCHAR(2000000),
  "version" VARCHAR(2000000),
  "created" TIMESTAMP(3),
  "updated" TIMESTAMP(3),
  "user_id" VARCHAR(2000000),
  "current_stage" VARCHAR(2000000),
  "description" VARCHAR(2000000),
  "source" VARCHAR(2000000),
  "run_id" VARCHAR(2000000),
  "status" VARCHAR(2000000),
  "status_message" VARCHAR(2000000),
  "run_link" VARCHAR(2000000),
  "aliases" VARCHAR(2000000),
  "model_id" VARCHAR(2000000),
  "tag_key" VARCHAR(2000000),
  "tag_value" VARCHAR(2000000)
) AS
from exasol.mlflow_plugin import rest_api

udf_call = rest_api.UdfCall(exa, endpoint=rest_api.MODEL_VERSIONS_SEARCH)

def run(ctx):
    udf_call.run(ctx)
/ 

--/
CREATE OR REPLACE MLFLOW SCALAR SCRIPT "REGISTERED_MODEL_GET" (
  "connection_name" VARCHAR(2000000),
  "name" VARCHAR(2000000)
) EMITS (
  "name" VARCHAR(2000000),
  "created" TIMESTAMP(3),
  "updated" TIMESTAMP(3),
  "user_id" VARCHAR(2000000),
  "description" VARCHAR(2000000),
  "deployment_job_id" VARCHAR(2000000),
  "deployment_job_state" VARCHAR(2000000),
  "tag_key" VARCHAR(2000000),
  "tag_value" VARCHAR(2000000)
) AS
from exasol.mlflow_plugin import rest_api

udf_call = rest_api.UdfCall(exa, endpoint=rest_api.REGISTERED_MODEL_GET)

def run(ctx):
    udf_call.run(ctx)
/ 

--/
CREATE OR REPLACE MLFLOW SCALAR SCRIPT "REGISTERED_MODELS_SEARCH" (
  "connection_name" VARCHAR(2000000),
  "filter" VARCHAR(2000000),
  "order_by" VARCHAR(2000000),
  "max_results" DECIMAL(18,0)
) EMITS (
  "name" VARCHAR(2000000),
  "created" TIMESTAMP(3),
  "updated" TIMESTAMP(3),
  "user_id" VARCHAR(2000000),
  "description" VARCHAR(2000000),
  "deployment_job_id" VARCHAR(2000000),
  "deployment_job_state" VARCHAR(2000000),
  "tag_key" VARCHAR(2000000),
  "tag_value" VARCHAR(2000000)
) AS
from exasol.mlflow_plugin import rest_api

udf_call = rest_api.UdfCall(exa, endpoint=rest_api.REGISTERED_MODELS_SEARCH)

def run(ctx):
    udf_call.run(ctx)
/ 

--/
CREATE OR REPLACE MLFLOW SCALAR SCRIPT "REGISTERED_MODELS_GET_LATEST_VERSIONS" (
  "connection_name" VARCHAR(2000000),
  "name" VARCHAR(2000000),
  "stages" VARCHAR(2000000)
) EMITS (
  "name" VARCHAR(2000000),
  "version" VARCHAR(2000000),
  "created" TIMESTAMP(3),
  "updated" TIMESTAMP(3),
  "user_id" VARCHAR(2000000),
  "current_stage" VARCHAR(2000000),
  "description" VARCHAR(2000000),
  "source" VARCHAR(2000000),
  "run_id" VARCHAR(2000000),
  "status" VARCHAR(2000000),
  "status_message" VARCHAR(2000000),
  "run_link" VARCHAR(2000000),
  "aliases" VARCHAR(2000000),
  "model_id" VARCHAR(2000000),
  "tag_key" VARCHAR(2000000),
  "tag_value" VARCHAR(2000000)
) AS
from exasol.mlflow_plugin import rest_api

udf_call = rest_api.UdfCall(exa, endpoint=rest_api.REGISTERED_MODELS_GET_LATEST_VERSIONS)

def run(ctx):
    udf_call.run(ctx)
/ 

--/
CREATE OR REPLACE MLFLOW SCALAR SCRIPT "RUNS_SEARCH" (
  "connection_name" VARCHAR(2000000),
  "experiment_ids" VARCHAR(2000000),
  "filter" VARCHAR(2000000),
  "run_view_type" VARCHAR(2000000),
  "order_by" VARCHAR(2000000),
  "max_results" DECIMAL(18,0)
) EMITS (
  "run_id" VARCHAR(2000000),
  "run_uuid" VARCHAR(2000000),
  "run_name" VARCHAR(2000000),
  "experiment_id" VARCHAR(2000000),
  "user_id" VARCHAR(2000000),
  "status" VARCHAR(2000000),
  "start_time" TIMESTAMP(3),
  "end_time" TIMESTAMP(3),
  "artifact_uri" VARCHAR(2000000),
  "lifecycle_stage" VARCHAR(2000000),
  "tag_key" VARCHAR(2000000),
  "tag_value" VARCHAR(2000000)
) AS
from exasol.mlflow_plugin import rest_api

udf_call = rest_api.UdfCall(exa, endpoint=rest_api.RUNS_SEARCH)

def run(ctx):
    udf_call.run(ctx)
/ 

--/
CREATE OR REPLACE MLFLOW ADAPTER SCRIPT
  "MLFLOW_VIRTUAL_SCHEMA_ADAPTER" AS
from exasol.mlflow_plugin.rest_api.vs_impl import RequestHandler

HANDLER = RequestHandler(exa.meta)

def adapter_call(request_str):
    return HANDLER.handle(request_str)
/
