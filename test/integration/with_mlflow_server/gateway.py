from typing import Any

import docker
from docker.models.containers import Container as DockerContainer
from exasol.pytest_backend.itde import OnpremDBConfig
from exasol_integration_test_docker_environment.lib.models.data.environment_info import (
    EnvironmentInfo,
)


def exposes_port(container: DockerContainer, port: int) -> bool:
    """
    Check whether the provided Docker container exposes the specified port.
    """
    port_config = {}
    if network := container.attrs.get("NetworkSettings"):
        port_config = network.get("Ports", {})
    for _, forwards in port_config.items():
        for el in forwards:
            if el.get("HostPort") == str(port):
                return True
    return False


def first_gateway(container: DockerContainer) -> str | None:
    """
    Return the first gateway set in the network settings for the specified
    Docker container or None if there is not any network specifying a gateway.
    """
    networks = container.attrs.get("NetworkSettings", {}).get("Networks", {})
    first: dict[str, Any] = next(iter(networks.values()), {})
    return first.get("Gateway", None)


def find_gateway(itde_info: EnvironmentInfo, request) -> str | None:
    """
    Return the ip address of the network gateway of the Exasol database.

    * In case the database is launched by ITDE, the gateway can be taken from
      the EnvironmentInfo provided by the ITDE.

    * In case the user uses an external database, try to inquire the gateway
      via the Docker client.
    """
    if tracking_uri := request.config.getoption("--mlflow-tracking-uri"):
        return tracking_uri
    return itde_info.network_info.gateway


def find_gateway_old(
    itde_info: EnvironmentInfo, exasol_config: OnpremDBConfig
) -> str | None:
    """
    Return the ip address of the network gateway of the Exasol database.

    * In case the database is launched by ITDE, the gateway can be taken from
      the EnvironmentInfo provided by the ITDE.

    * In case the user uses an external database, try to inquire the gateway
      via the Docker client.
    """
    if itde_info:
        return itde_info.network_info.gateway
    client = docker.from_env()
    matching = (
        c for c in client.containers.list() if exposes_port(c, exasol_config.port)
    )
    if container := next(matching, None):
        return first_gateway(container)
    return None
