# 1.0.0 - 2026-03-06

## Summary

This is the initial release of Exasol MLflow Plugin. Please see the user guide for installation, getting started, and additional information on using this plugin.

## Features

* #3: Added initial plugin configuration and empty interface extending `ArtifactRepository`
* #6: Added parsing the BucketFS parameters from MLflow `artifact_root` string
* #8: Added implementation to interface `BucketFsArtifactRepo`, incl. simple itests
* #27: Prepared release `1.0.0`

## Documentation

* #14: Added User Guide and Developer Guide
* #17: Added required scope of plugin availability to the User Guide
* #25: Described MLflow access from UDFs in the User Guide
* #33: Added to the User Guide how to create MLflow experiments

## Refactorings

* #9: Refactored bucketfs_spec, added class Connector
* #12: Added end-to-end tests incl. MLflow server
* #19: Added SLC building to integration tests
* #23: Created UDFs for itests
* #29: Integrated new version of `exasol-bucketfs`
* #31: Updated Python Toolbox and re-generated GitHub workflows
* #26: Changed visibility of GitHub project to public

## Dependency Updates

### `main`

* Added dependency `exasol-bucketfs:2.2.0`
* Added dependency `mlflow:3.10.0`

### `dev`

* Added dependency `exasol-python-extension-common:0.13.0`
* Added dependency `exasol-toolbox:6.0.0`
* Added dependency `pytest-exasol-backend:1.4.0`
* Added dependency `pytest-exasol-slc:0.4.4`
