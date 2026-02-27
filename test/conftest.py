def pytest_addoption(parser):
    parser.addoption(
        "--mlflow-server",
        type=str,
        help=(
            "If this option is specified, then instead of starting an "
            "MLflow server, pytest will reuse the server already running at "
            "the specified URL, e.g. http://localhost:5000."
        ),
    )
