import logging

import exasol.bucketfs as bfs
import mlflow
from mlflow.entities import FileInfo
from sklearn.linear_model import LogisticRegression

from exasol.mlflow_plugin.artifacts.repo import bfs_location

mlflow.set_tracking_uri("http://localhost:5000")


# LOG = logging.getLogger(__name__)
# logging.basicConfig(
#     level=logging.INFO,
#     format="[%(levelname)s] %(message)s",
# )

logging.getLogger("exasol.bucketfs").setLevel(logging.WARN)


def store_model():
    from exasol.mlflow_plugin.experiment import training_data as td

    lr = LogisticRegression(**td.params)
    # from mlflow.models.model import ModelInfo
    info = mlflow.sklearn.log_model(lr, name="my_first_logistic_regression")
    # ID: m-4d89d821f3da4c62a0e4c69d5ac63994,
    # artifact_path: exa+bfs://localhost:2580/bfsdefault/default/my_path/
    #                0/models/m-4d89d821f3da4c62a0e4c69d5ac63994/artifacts

    # mlflow.models.Model.load(uri)
    print(f"ID: {info.model_id}, artifact_path: {info.artifact_path}")
    bfsloc = bfs_location(info.artifact_path)

    for f in bfsloc.iterdir():
        print(f"- {f.name}")
    # Expected files:
    # - conda.yaml
    # - python_env.yaml
    # - model.pkl
    # - MLmodel
    # - requirements.txt


def list_model():
    artifact_uri = (
        "exa+bfs://localhost:2580/bfsdefault/default/my_path/"
        "0/models/m-0e8d6aa6c8f1492e9d292f1b56f2ef4c/artifacts"
    )
    bfsloc = bfs_location(artifact_uri)
    for f in bfsloc.iterdir():
        print(f"- {f.name}")


def upload_to_bucketfs():
    import sys

    file = sys.argv[1]
    print(f"uploading {file}")
    bfsloc = bfs_location("exa+bfs://localhost:2580/bfsdefault/default")
    dest = bfsloc / "file.txt"
    with open(file, "rb") as fd:
        dest.write(fd)
    for f in bfsloc.iterdir():
        print(f"{f}")


def list_bfs():
    from mlflow.entities import FileInfo

    bfsloc = bfs_location("exa+bfs://localhost:2580/bfsdefault/default")
    path = None
    result = []

    def info(root: bfs.path.PathLike, name: str, is_dir: bool):
        full_path = (path / root if path else root) / name
        print(f"listing {full_path}")
        return FileInfo(path=full_path, is_dir=is_dir, file_size=None)

    def dir_info(root: bfs.path.PathLike, name: str):
        return info(root, name, is_dir=True)

    def file_info(root: bfs.path.PathLike, name: str):
        return info(root, name, is_dir=False)

    for root, dirs, files in bfsloc.walk():
        result += [dir_info(root, x) for x in dirs]
        result += [file_info(root, x) for x in files]

    return result


def experiment_2():
    result = list_bfs()
    fi = FileInfo("abc", is_dir=False, file_size=None)
    print(f"{fi.path}")
    print(f"{fi.to_proto()}")


def main():
    store_model()
    # list_model()


if __name__ == "__main__":
    main()
