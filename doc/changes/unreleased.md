# Unreleased

## Summary

This release fixes vulnerabilities by updating transitive dependencies in the `poetry.lock` file.

| Name         | Version | ID             | Fix Versions | Updated to |
|--------------|---------|----------------|--------------|------------|
| black        | 25.12.0 | CVE-2026-32274 | 26.3.1       | 26.3.1     |
| cryptography | 46.0.5  | CVE-2026-34073 | 46.0.6       | 46.0.7     |
| pyasn1       | 0.6.2   | CVE-2026-30922 | 0.6.3        | 0.6.3      |
| pygments     | 2.19.2  | CVE-2026-4539  | 2.20.0       | 2.20.0     |
| requests     | 2.32.5  | CVE-2026-25645 | 2.33.0       | 2.33.1     |

To ensure usage of secure packages, it is up to the user to similarly relock their dependencies.

## Documentation

* #43: Added overview images to the User Guide

## Security

* #48: Relocked vulnerable transitive and dev dependencies