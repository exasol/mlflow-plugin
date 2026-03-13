ENV_BUCKETFS_USER = "EXA_BUCKETFS_USER"
"""
Name of the environment variable containing the user name for writing to
the BucketFS of an Exasol On-premise instance.
"""
# Ignore bandit finding, as this is not a password but the name of an
# environment variable.
ENV_BUCKETFS_PASSWORD = "EXA_BUCKETFS_PASSWORD"  # nosec: B105
"""
Name of the environment variable containing the password for writing to
the BucketFS of an Exasol On-premise instance.
"""
ENV_SSL_CERT_VALIDATION = "EXA_SSL_CERT_VALIDATION"
"""
Name of the environment variable specifying
whether the validity of SSL certificates should be verified.

Supported values: ``yes``, ``no``, ``y``, ``n``, ``true``, ``false``
(case-insensitive).
"""


def str_to_bool(s: str) -> bool:
    s_lower = s.lower()
    if s_lower in ["true", "yes", "y"]:
        return True
    if s_lower in ["false", "no", "n"]:
        return False
    raise ValueError(f"Invalid boolean parameter: {s}")
