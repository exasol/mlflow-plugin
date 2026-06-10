from exasol.mlflow_plugin.rest_api.data import Column

SEARCH_COLUMNS = [
    Column.varchar("filter"),
    Column.varchar("order_by", comma_sep=True),
    Column.decimal("max_results"),
]
