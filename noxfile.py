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
    Builds and exports an SLC Image to directory ``.slc``
    """
    export_path = PROJECT_CONFIG.root_path / ".slc"
    with slc_build_context() as builder:
        builder.export(export_path)
