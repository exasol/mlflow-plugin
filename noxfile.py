import nox

# imports all nox task provided by the toolbox
from exasol.toolbox.nox.tasks import *

from exasol.mlflow_plugin.slc import slc_build_context

# default actions to be run if nothing is explicitly specified with the -s option
nox.options.sessions = ["format:fix"]

from noxconfig import PROJECT_CONFIG


@nox.session(name="slc:export", python=False)
def slc_export(session: nox.Session):
    """
    Build and export an SLC Image to directory ``.slc``.
    """
    export_path = PROJECT_CONFIG.root_path / ".slc"
    with slc_build_context() as builder:
        builder.export(export_path)


@nox.session(name="slc:activation", python=False)
def slc_activation(session: nox.Session):
    """
    Display the activation command for the SLC.
    """
    export_path = PROJECT_CONFIG.root_path / ".slc"
    suffix = ".tar.gz"
    stem = next(export_path.glob(f"*{suffix}")).name.removesuffix(suffix)
    bfspath = "bfsdefault/default"
    prefix = "PYTHON3=builtin_python3 R=builtin_r JAVA=builtin_java"
    udf_client_binary = "udfclient"
    sql = (
        "ALTER SYSTEM SET SCRIPT_LANGUAGES"
        f"='{prefix} MLFLOW=localzmq+protobuf:///{bfspath}/{stem}?"
        f"lang=python#buckets/{bfspath}/{stem}/exaudf/{udf_client_binary}';"
    )
    print(
        "Use the following SQL command",
        "to active the Script language alias MLFLOW:\n\n",
        sql
    )
