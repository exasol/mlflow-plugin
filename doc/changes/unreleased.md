# Unreleased

## Summary

## Features

* #3: Added initial plugin configuration and empty interface extending `ArtifactRepository`
* #6: Added parsing the BucketFS parameters from MLflow `artifact_root` string
* #8: Added implementation to interface BucketFsArtifactRepo, incl. simple itests

## Documentation

* #14: Added User Guide and Developer Guide
* #17: Added required scope of plugin availability to the User Guide

## Refactorings

* #9: Refactored bucketfs_spec, added class Connector
* #12: Added end-to-end tests incl. MLflow server
