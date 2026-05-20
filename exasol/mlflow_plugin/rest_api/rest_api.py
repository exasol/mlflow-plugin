import logging
from collections.abc import (
    Generator,
    Iterable,
)
from typing import Any

import requests

from exasol.mlflow_plugin.rest_api.column import Column

LOG = logging.getLogger(__name__)
TIMEOUT_IN_SECONDS = 5

JsonData = dict[str, Any] | list[Any]
JsonObject = dict[str, Any]


class MLflowRestApi:
    DEFAULT_TAGS = [{"key": None, "value": None}]
    TAG_COLUMNS = [
        Column("tag_key", 15, align="right"),
        Column("tag_value", 15),
    ]

    def __init__(
        self,
        endpoint: str,
        params: JsonObject,
        key: str,
        has_tags: bool,
        columns: list[Column],
    ):
        self.endpoint = endpoint
        self.params = params
        self.key = key
        self.has_tags = has_tags
        self.columns = columns + self.TAG_COLUMNS if has_tags else columns

    @property
    def header(self) -> str:
        data = {c.name: c.header for c in self.columns}
        return (
            self.format(data, body=False)
            + "\n"
            + "-".join("-" * c.width for c in self.columns)
        )

    def format(self, data: JsonObject, body: bool = True) -> str:
        return " ".join(c.format(data.get(c.name), body) for c in self.columns)

    def sql(self, data: JsonObject) -> list[Any]:
        return [c.sql(data.get(c.name)) for c in self.columns]

    def _process(self, data: Iterable[JsonObject]) -> Generator[JsonObject]:
        if self.has_tags:
            data = (
                el | {"tag_key": tag["key"], "tag_value": tag["value"]}
                for el in data
                for tag in el.get("tags", self.DEFAULT_TAGS)
            )

        yield from data

    def result(self) -> Generator[JsonObject]:
        page_token = ""  # nosec: B105 - this is not an actual token
        while page_token is not None:
            query = self.params | {"page_token": page_token}
            raw_respose = requests.post(
                self.endpoint,
                json=query,
                timeout=TIMEOUT_IN_SECONDS,
            )
            resp = raw_respose.json()
            yield from self._process(resp.get(self.key, []))
            page_token = resp.get("next_page_token")
            LOG.debug(f"retrieving page {page_token}")
