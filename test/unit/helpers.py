import contextlib

import pytest


@contextlib.contextmanager
def not_raises(exception_class):
    def all_causes(ex):
        while ex.__cause__:
            ex = ex.__cause__
            yield f"\n- caused by {type(ex).__name__}: {ex}"

    try:
        yield
    except exception_class as ex:
        causes = "".join(all_causes(ex))
        raise pytest.fail(
            f"Test raised unexpected {exception_class.__name__}: {ex}{causes}"
        )
