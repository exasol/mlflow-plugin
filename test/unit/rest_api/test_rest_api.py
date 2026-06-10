from collections.abc import Callable
from unittest.mock import Mock

import pytest

from exasol.mlflow_plugin.rest_api import rest_api
from exasol.mlflow_plugin.rest_api.data import JsonObject

KEY = "experiments"

ANSWERS = [
    {KEY: list("ab"), "next_page_token": "2"},
    {KEY: list("cd")},
]


@pytest.fixture
def endpoint() -> rest_api.MLflowRestApi:
    return rest_api.MLflowRestApi("post", "endpoint", KEY, None)


@pytest.fixture
def mock_requests(monkeypatch) -> Callable[[str, list[JsonObject]], Mock]:
    def func(target: str, return_values: list[JsonObject]) -> Mock:
        def response(value):
            response = Mock()
            response.json.return_value = value
            response.status_code = 200
            return response

        post = Mock()
        post.side_effect = [response(v) for v in return_values]
        monkeypatch.setattr(rest_api.requests, target, post)
        return post

    return func


def test_paging(endpoint, mock_requests) -> None:
    mock = mock_requests("request", ANSWERS)
    actual = list(endpoint.call({}))
    assert mock.call_count == 2
    assert actual == list("abcd")
