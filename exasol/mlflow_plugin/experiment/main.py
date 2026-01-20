import logging

import mlflow
from sklearn.linear_model import LogisticRegression


mlflow.set_tracking_uri("http://localhost:5000")


LOG = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)


def store_model():
    from exasol.mlflow_plugin.experiment import training_data as td
    mlflow.sklearn.autolog()

    lr = LogisticRegression(**td.params)
    # mlflow.sklearn.save_model(lr, "lr-model")
    lr.fit(td.X_train, td.y_train)


if __name__ == "__main__":
    store_model()
