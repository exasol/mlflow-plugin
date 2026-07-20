def pytest_addoption(parser):
    """
    See details in the developer guide.
    """

    parser.addoption(
        "--mlflow-server",
        type=str,
        help=(
            "If this option is specified, then instead of starting an "
            "MLflow server, pytest will reuse the server already running at "
            "the specified URL, e.g. http://localhost:5000."
        ),
    )
    parser.addoption(
        "--language-alias",
        type=str,
        help=("Can be set to override the default. The default is MLFLOW."),
    )
    parser.addoption(
        "--db-schema",
        type=str,
        help=("Can be set to override the default. The default is ITEST_MLFLOW."),
    )
    parser.addoption(
        "--keep-virtual-schema",
        action="store_true",
        help=("Keep the virtual schema after the tests have completed."),
    )
