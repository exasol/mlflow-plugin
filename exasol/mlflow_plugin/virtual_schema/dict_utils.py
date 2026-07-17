from typing import Any


def dget(req: dict[str, Any], *keys: str, default: Any = None) -> Any:
    """
    Return the value addressed by the specified sequence of keys pointing
    into potentially nested dicts. If one of the keys is not contained, then
    return the specified default value.

    Args:

       req: dict to search in

       default: default value to return in case any of the keys is not found

       keys: sequence of keys to look for in potentially nested dict ``req``.
    """

    current: Any = req
    for k in keys:
        if not (current := current.get(k)):
            return default
    return current
