import logging

import mlflow
from sklearn.linear_model import LogisticRegression

from exasol.mlflow_plugin.artifacts.bucketfs_spec import bucketfs_parameters
from exasol.mlflow_plugin.connections import bucketfs_location

mlflow.set_tracking_uri("http://localhost:5000")


# LOG = logging.getLogger(__name__)
# logging.basicConfig(
#     level=logging.INFO,
#     format="[%(levelname)s] %(message)s",
# )


def store_model():
    from exasol.mlflow_plugin.experiment import training_data as td
    mlflow.sklearn.autolog()

    lr = LogisticRegression(**td.params)
    # mlflow.sklearn.save_model(lr, "lr-model")
    lr.fit(td.X_train, td.y_train)


def upload_to_bucketfs():
    params = bucketfs_parameters("bfs://localhost:2580/bfsdefault/default")
    bfsloc = bucketfs_location(params)
    print(f'{params}')


def main():
    # store_model()
    upload_to_bucketfs()


if __name__ == "__main__":
    main()
