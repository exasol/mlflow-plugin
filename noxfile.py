import jinja2
import nox

# imports all nox task provided by the toolbox
from exasol.toolbox.nox.tasks import *

from exasol.mlflow_plugin.rest_api.udf.deployment import (
    ALL_ENDPOINTS,
    Deployable,
)
from exasol.mlflow_plugin.slc import slc_build_context

# default actions to be run if nothing is explicitly specified with the -s option
nox.options.sessions = ["format:fix"]

from inspect import cleandoc
from pathlib import Path

from noxconfig import PROJECT_CONFIG


@nox.session(name="slc:export", python=False)
def slc_export(session: nox.Session):
    """
    Build and export an SLC Image to directory ``.slc``.
    """
    export_path = PROJECT_CONFIG.root_path / ".slc"
    with slc_build_context() as builder:
        builder.export(export_path)

ANCHORS = {
    "experiments/search": "search-experiments",
    "runs/search": "search-runs",
    "registered-models/search": "search-registeredmodels",
    "registered-models/get-latest-versions": "get-latest-modelversions",
    "registered-models/get": "get-registeredmodel",
    "model-versions/search": "search-modelversions",
    "model-versions/get": "get-modelversion",
    "model-versions/get-download-uri": "get-download-uri-for-modelversion-artifacts",
    "gateway/endpoints/list": "list-gateway-endpoints",
    "gateway/model-definitions/list": "list-gateway-model-definitions",
    "artifacts": "mlflowartifactsmlflowartifactsservicelistartifacts",
}

@nox.session(name="docs:udfs", python=False)
def docs_update_udfs(session: nox.Session):
    """
    Update documentation on MLflow's REST API UDFs.
    """
    path = PROJECT_CONFIG.root_path / "doc/user_guide/access_mlflow"
    env = jinja2.Environment()
    tmpl_str = (path / "template_rest_endpoints.jinja").read_text()
    template = env.from_string(tmpl_str)
    with (path / "rest_endpoints.rst").open("w") as f:
        for ep in ALL_ENDPOINTS:
            args = ", ".join(col.name for col in ep.input_columns)
            input_columns = [(c.sql_name, c.sql_type) for c in ep.input_columns]
            output_columns = [(c.sql_name, c.sql_type) for c in ep.total_output_columns]
            result = template.render(
                udf_name=ep.var_name,
                underline="-" * (len(ep.var_name) + 8),
                udf_args=args,
                endpoint=ep.url_suffix,
                anchor=ANCHORS[ep.url_suffix],
                input_columns=input_columns,
                output_columns=output_columns,
            )
            print(result, file=f)
