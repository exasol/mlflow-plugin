import datetime

import pytest

from exasol.mlflow_plugin.rest_api.data import Column


def test_default_values() -> None:
    column = Column("col", size=20)
    assert column == Column(
        "col", 20, sql_name="col", data_type=str, key="col", comma_sep=False
    )


def test_timestamp() -> None:
    column = Column.timestamp("col", sql_name="TIME")
    assert column == Column("col", 3, "TIME", datetime.datetime)
    dt = datetime.datetime.fromisoformat("2026-05-20 08:32:18+00:00")
    expected = dt.replace(tzinfo=None)
    assert column.process(dt.timestamp() * 1000) == expected
    assert column.sql == '"TIME" TIMESTAMP(3)'


def test_varchar() -> None:
    column = Column.varchar("col", sql_name="VVV")
    assert column == Column("col", 2000000, "VVV", str)
    assert column.sql == '"VVV" VARCHAR(2000000)'


def test_decimal() -> None:
    column = Column.decimal("col", precision=12, sql_name="DDD")
    assert column == Column("col", 12, "DDD", data_type=int)
    assert column.sql == '"DDD" DECIMAL(12,0)'


@pytest.mark.parametrize(
    "column, expected_json, expected_sql",
    [
        pytest.param(
            Column.decimal("col"),
            {
                "name": "col",
                "dataType": {"type": "DECIMAL", "precision": 18, "scale": 0},
            },
            '"col" DECIMAL(18,0)',
            id="decimal_with_defaults",
        ),
        pytest.param(
            Column.decimal("col", precision=12, sql_name="DDD"),
            {
                "name": "DDD",
                "dataType": {"type": "DECIMAL", "precision": 12, "scale": 0},
            },
            '"DDD" DECIMAL(12,0)',
            id="decimal_with_name_and_precision",
        ),
        pytest.param(
            Column.varchar("col"),
            {
                "name": "col",
                "dataType": {"type": "VARCHAR", "size": 2000000},
            },
            '"col" VARCHAR(2000000)',
            id="varchar_with_defaults",
        ),
        pytest.param(
            Column.varchar("col", size=33, sql_name="VVV"),
            {
                "name": "VVV",
                "dataType": {"type": "VARCHAR", "size": 33},
            },
            '"VVV" VARCHAR(33)',
            id="varchar_with_name_and_size",
        ),
        pytest.param(
            Column.timestamp("col"),
            {
                "name": "col",
                "dataType": {"type": "TIMESTAMP"},
            },
            '"col" TIMESTAMP(3)',
            id="timestamp",
        ),
    ],
)
def test_rendering(column, expected_json, expected_sql) -> None:
    assert column.json == expected_json
    assert column.sql == expected_sql
