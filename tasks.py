import sys

from invoke import task


@task
def test(ctx):
    import pytest
    retcode = pytest.main([])
    sys.exit(retcode)
