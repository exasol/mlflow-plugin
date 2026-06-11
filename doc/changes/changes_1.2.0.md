# 2.0.0 - 2026-06-11

## Summary

This release adds UDFs for querying MLflow's REST API from Exasol SQL.

The updated Documentation contains instructions for accessing the
* MLflow Backend Store via an Exasol Virtual Schema and the
* MLflow AI Gateway from UDFs.

It also describes the [REST API UDFs](https://exasol.github.io/mlflow-plugin/main/user_guide/access_mlflow/rest_api.html) and has been reorganized for better orientation and quicker lookup.

Additionally, this release fixes vulnerabilities by updating dependencies.

## Security Issues

This release fixes vulnerabilities by updating dependencies:

| Dependency | Vulnerability | Affected | Fixed in |
|------------|---------------|----------|----------|
| black | CVE-2026-32274 | 25.12.0 | 26.3.1 |
| cryptography | PYSEC-2026-35 | 46.0.5 | 46.0.6 |
| cryptography | PYSEC-2026-36 | 46.0.5 | 46.0.7 |
| cryptography | PYSEC-2026-36 | 46.0.5 | 46.0.7 |
| cryptography | PYSEC-2026-35 | 46.0.5 | 46.0.6 |
| gitpython | CVE-2026-42215 | 3.1.46 | 3.1.47 |
| gitpython | CVE-2026-42284 | 3.1.46 | 3.1.47 |
| gitpython | CVE-2026-44244 | 3.1.46 | 3.1.49 |
| gitpython | GHSA-mv93-w799-cj2w | 3.1.46 | 3.1.50 |
| idna | CVE-2026-45409 | 3.11 | 3.15 |
| mako | CVE-2026-44307 | 1.3.10 | 1.3.12 |
| mlflow | PYSEC-2026-94 | 3.10.1 | 3.11.0rc0 |
| mlflow | PYSEC-2026-93 | 3.10.1 | 3.11.1 |
| mlflow | PYSEC-2026-94 | 3.10.1 | 3.11.0rc0 |
| mlflow | PYSEC-2026-93 | 3.10.1 | 3.11.0rc0 |
| mlflow | CVE-2026-2652 | 3.10.1 | 3.11.0 |
| mlflow | CVE-2026-4137 | 3.10.1 | 3.11.0 |
| pillow | PYSEC-2026-165 | 12.1.1 | 12.2.0 |
| pillow | PYSEC-2026-165 | 12.1.1 | 12.2.0 |
| pillow | CVE-2026-40192 | 12.1.1 | 12.2.0 |
| pillow | CVE-2026-42309 | 12.1.1 | 12.2.0 |
| pillow | CVE-2026-42310 | 12.1.1 | 12.2.0 |
| pillow | CVE-2026-42311 | 12.1.1 | 12.2.0 |
| pip | PYSEC-2026-196 | 26.0.1 | 26.1.2 |
| pip | CVE-2026-3219 | 26.0.1 | 26.1 |
| pip | CVE-2026-6357 | 26.0.1 | 26.1 |
| pyasn1 | CVE-2026-30922 | 0.6.2 | 0.6.3 |
| pygments | CVE-2026-4539 | 2.19.2 | 2.20.0 |
| pytest | CVE-2025-71176 | 8.4.2 | 9.0.3 |
| requests | CVE-2026-25645 | 2.32.5 | 2.33.0 |
| starlette | PYSEC-2026-161 | 0.52.1 | 1.0.1 |
| starlette | PYSEC-2026-161 | 0.52.1 | 1.0.1 |
| urllib3 | PYSEC-2026-142 | 2.6.3 | 2.7.0 |
| urllib3 | PYSEC-2026-142 | 2.6.3 | 2.7.0 |
| urllib3 | PYSEC-2026-141 | 2.6.3 | 2.7.0 |

## Features

* #53: Added REST API calls for experiments/search (Layer 1)
* #56: Created a UDF for the REST API endpoint `experiments/search`
* #68: Added remaining endpoints of MLflow REST API

## Documentation

* #43: Added overview images to the User Guide
* #59: Added documentation for Virtual Schema Access to the MLflow database
* #61: Added documentation for accessing MLflow AI Gateway endpoints from UDFs
* #70: Reorganized documentation structure
* #72: Added documentation for the REST API UDFs

## Security

* #48: Relocked vulnerable transitive and dev dependencies
* #51: Fixed vulnerabilities by updating dependencies
* #58: Fixed vulnerabilities by updating dependencies

## Dependency Updates

### `main`

* Updated dependency `mlflow:3.10.1` to `3.11.1`
* Added dependency `mlflow-skinny:3.11.1`

### `dev`

* Updated dependency `exasol-python-extension-common:0.13.0` to `0.15.0`
* Updated dependency `exasol-toolbox:6.0.0` to `8.2.0`
* Added dependency `jinja2:3.1.6`
* Updated dependency `pytest-exasol-backend:1.4.0` to `1.4.1`
* Updated dependency `pytest-exasol-slc:0.4.4` to `1.0.1`
