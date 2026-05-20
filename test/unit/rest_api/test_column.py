import pytest

from exasol.mlflow_plugin.rest_api.column import Column


def test_default_values() -> None:
    column = Column("col_suffix", width=20)
    assert column == Column("col_suffix", 20, "Col Suffix", "", "left")


@pytest.mark.parametrize(
    "value, expected",
    [
        ("short", "short "),
        ("long value ", "long v"),
        (123456789123456789, "123456"),
    ],
)
def test_format(value, expected) -> None:
    column = Column("col", width=6)
    assert column.format(value) == expected


def test_align_right() -> None:
    column = Column("col", width=6, align="right")
    assert column.format("short") == " short"


def test_timestamp() -> None:
    column = Column.timestamp("col", header="Time")
    assert column == Column("col", 20, "Time", "timestamp", "left")
    assert column.format(1779258738 * 1000) == "2026-05-20 06:32:18 "
