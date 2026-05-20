from typing import (
    Any,
    Iterable,
)

from exasol.mlflow_plugin.rest_api.data import (
    Column,
    JsonObject,
)


class PostProcessor:
    """
    Process the generic Json response
    """

    DEFAULT_TAGS = [{"key": None, "value": None}]
    TAG_COLUMNS = [
        Column("tag_key", 15, align="right"),
        Column("tag_value", 15),
    ]

    def __init__(self, has_tags: bool, columns: list[Column]):
        self.has_tags = has_tags
        self.columns = columns + self.TAG_COLUMNS if has_tags else columns

    def _expand(self, data: Iterable[JsonObject]) -> Iterable[JsonObject]:
        if not self.has_tags:
            return data
        return (
            el | {"tag_key": tag["key"], "tag_value": tag["value"]}
            for el in data
            for tag in el.get("tags", self.DEFAULT_TAGS)
        )

    def process(self, data: Iterable[JsonObject]) -> Iterable[list[Any]]:
        return (
            [c.process(el.get(c.name)) for c in self.columns]
            for el in self._expand(data)
        )
