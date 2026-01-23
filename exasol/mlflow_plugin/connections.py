import exasol.bucketfs as bfs


def bucketfs_location(params: dict[str, str | bool]) -> bfs.path.PathLike:
    return bfs.path.build_path(**params)
