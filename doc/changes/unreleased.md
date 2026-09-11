# Unreleased

## Summary

This release adds support for accessing the MLflow REST API via an Exasol Virtual Schema. It also fixes a bug where array values returned by the REST API were not correctly converted to comma-separated strings.

## Features

* #84: Render `Column` as Json as required for Virtual Schema API
* #90: Configured names of Virtual Schema tables
* #91: Added basic functions for Virtual Schema management
* #96: Added `AdapterProperties`
* #99: Added RequestHandler
* #103: Added Virtual Schema custom implementation for MLflow REST API
* #95: Supported attribute `comma_sep` for array values returned by REST API
* #101: Replaced `AdapterProperties` by `PropertyValidator`
* #114: Added class `TableRewriterWithSubQuery`
* #97: Handled mandatory parameters for specific UDFs

## Bugfixes

* #140: Fixed array values returned by REST API are now comma-separated
* #128: Fixed generated UDF documentation

## Documentation

* #88: Added information about which UDF input parameters are mandatory
* #117: Described Virtual Schema deployment in the user guide

## Refactoring

* #77: Updated workflows to `exasol-toolbox` 8.2.0
* #81: Update workflows to `exasol-toolbox` 10.0.0
* #82: Moved constant `ALL_ENDPOINTS` to package `rest_api`
* #86: Added pytest CLI option `--db-schema`
* #106: Changed interface of `RequestHandler`
* #109: Added integration tests for Virtual Schema implementation
* #110: Added class `QueryRewriter`
* #112: Added class `TableRewriter`
* #126: Moved deployment scripts into one single place, i.e. directory `exasol/mlflow_plugin/deploy`
* #121: Added integration test for deployment script
* #122: Added CI check to verify generated parts of the documentation are up-to-date
* #133: Updated to `exasol-toolbox` 10.4.0