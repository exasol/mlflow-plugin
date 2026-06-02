import contextlib
from test.unit.rest_api.udf.mocking import mock_exa_object

import pytest

from exasol.mlflow_plugin import rest_api
from exasol.mlflow_plugin.rest_api.data import Column
from exasol.mlflow_plugin.rest_api.udf.verification import (
    ExaMetaColumn,
    UdfParameterException,
    verify_columns,
    verify_udf_parameters,
)


@contextlib.contextmanager
def not_raises(exception):
    try:
        yield
    except exception:
        raise pytest.fail(f"Did raise {exception}")


@pytest.mark.parametrize(
    "actual, expected",
    [
        pytest.param(
            [ExaMetaColumn("a", "DECIMAL(18,0)"), ExaMetaColumn("b", "DECIMAL(18,0)")],
            [Column.decimal("a")],
            id="2_actual_1_expected",
        ),
        pytest.param(
            [ExaMetaColumn("a", "DECIMAL(18,0)")],
            [Column.decimal("a"), Column.decimal("b")],
            id="1_actual_2_expected",
        ),
        pytest.param(
            [ExaMetaColumn("a", "VARCHAR(200)")],
            [Column.varchar("b", 200)],
            id="name_mismatch",
        ),
        pytest.param(
            [ExaMetaColumn("a", "DECIMAL")],
            [Column.varchar("a", 200)],
            id="decimal_varchar",
        ),
        pytest.param(
            [ExaMetaColumn("a", "VARCHAR(200)")],
            [Column.decimal("a")],
            id="varchar_decimal",
        ),
        pytest.param(
            [ExaMetaColumn("a", "VARCHAR(200)")],
            [Column.varchar("a", 201)],
            id="size",
        ),
        pytest.param(
            [ExaMetaColumn("a", "DECIMAL(18,0)")],
            [Column.decimal("a", 17)],
            id="precision",
        ),
        pytest.param(
            [ExaMetaColumn("a", "DECIMAL(10,2)")],
            [Column.decimal("a", 10)],
            id="scale",
        ),
    ],
)
def test_verify_columns_fails(actual, expected) -> None:
    with pytest.raises(UdfParameterException):
        verify_columns("input", actual, expected)


@pytest.mark.parametrize(
    "actual, expected",
    [
        pytest.param(
            [ExaMetaColumn("a", "DECIMAL(18,0)")],
            [Column.decimal("a")],
            id="decimal",
        ),
        pytest.param(
            [ExaMetaColumn("a", "VARCHAR(200)")],
            [Column.varchar("a", 200)],
            id="varchar",
        ),
        pytest.param(
            [ExaMetaColumn("a", "VARCHAR(200)"), ExaMetaColumn("b", "DECIMAL(10,0)")],
            [Column.varchar("a", 200), Column.decimal("b", 10)],
            id="2-columns",
        ),
    ],
)
def test_verify_columns_success(actual, expected) -> None:
    with not_raises(UdfParameterException):
        verify_columns("output", actual, expected)


def test_verify_udf_parameters_success():
    endpoint = rest_api.EXPERIMENTS_SEARCH
    exa_meta = mock_exa_object(endpoint).meta
    with not_raises(UdfParameterException):
        verify_udf_parameters(exa_meta, endpoint)


def test_verify_udf_parameters_fails():
    endpoint = rest_api.EXPERIMENTS_SEARCH
    exa_meta = mock_exa_object(endpoint).meta
    exa_meta.input_columns = exa_meta.input_columns[1:]
    with pytest.raises(UdfParameterException):
        verify_udf_parameters(exa_meta, endpoint)
