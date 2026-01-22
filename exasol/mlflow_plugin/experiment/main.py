import logging

import mlflow
from sklearn.linear_model import LogisticRegression
from mlflow.entities import FileInfo

from exasol.mlflow_plugin.artifacts.bucketfs_spec import bucketfs_parameters
from exasol.mlflow_plugin.connections import bucketfs_location
from exasol.mlflow_plugin.artifacts.repo import bfs_location
import exasol.bucketfs as bfs

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
    import sys
    file = sys.argv[1]
    print(f'uploading {file}')

    params = bucketfs_parameters("exa+bfs://localhost:2580/bfsdefault/default")
    bfsloc = bucketfs_location(params)
    print(f'{params}')

    dest = bfsloc / "file.txt"
    # dest.write(b"123")
    with open(file, "rb") as fd:
        dest.write(fd)
    for f in bfsloc.iterdir():
        print(f'{f}')

def list_bfs():
    from mlflow.entities import FileInfo
    bfsloc = bfs_location("exa+bfs://localhost:2580/bfsdefault/default")
    path = None
    result = []

    def info(root: bfs.path.PathLike, name: str, is_dir: bool):
        full_path = (path / root if path else root) / name
        print(f'listing {full_path}')
        return FileInfo(path=full_path, is_dir=is_dir, file_size=None)

    def dir_info(root: bfs.path.PathLike, name: str):
        return info(root, name, is_dir=True)

    def file_info(root: bfs.path.PathLike, name: str):
        return info(root, name, is_dir=False)

    for root, dirs, files in bfsloc.walk():
        result += [dir_info(root, x) for x in dirs]
        result += [file_info(root, x) for x in files]

    return result


def main():
    store_model()
    return
    result = list_bfs()
    fi = FileInfo("abc", is_dir=False, file_size=None)
    print(f'{fi.path}')
    print(f'{fi.to_proto()}')


if __name__ == "__main__":
    main()
