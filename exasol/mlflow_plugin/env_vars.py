ENV_BUCKETFS_USER = "EXA_BUCKETFS_USER"
""" On-prem BucketFS user name """
# Ignore bandit finding, as this is not a password but the name of an
# environment variable.
ENV_BUCKETFS_PASSWORD = "EXA_BUCKETFS_PASSWORD"  # nosec: B105
""" On-prem BucketFS user password """
ENV_SSL_CERT_VALIDATION = "EXA_SSL_CERT_VALIDATION"
""" Verify other peers’ certificates (yes/no) """


def str_to_bool(s: str) -> bool:
    s_lower = s.lower()
    if s_lower in ["true", "yes", "y"]:
        return True
    if s_lower in ["false", "no", "n"]:
        return False
    raise ValueError(f"Invalid boolean parameter: {s}")
