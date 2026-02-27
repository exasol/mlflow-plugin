When and for Which Operations is the MLflow Plugin Required?
============================================================

The MLflow server can be started with ``--default-artifact-root`` but without any plugin.

Only the client code needs to implement the plugin or add it as a dependency

If the plugin is not installed, the server will show errors in the UI and log
messages only when navigating to a page listing the artifacts. Other functions
of the server are not affected.
