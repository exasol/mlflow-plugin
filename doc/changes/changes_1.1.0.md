# 1.1.0 - 2026-03-13

## Summary

This release adds convenience methods for loading an artifact from the BucketFS using the associated path mounted in local file system with fallback to loading the artifact via the URI (e.g. HTTP).

The updated User Guide describes and compares the different load alternatives incl. their performance and adds an API documentation.

## Features

* #38: Supported loading an artifact from BucketFS with fallback to HTTP

## Dependency Updates

### `main`

* Updated dependency `mlflow:3.10.0` to `3.10.1`
