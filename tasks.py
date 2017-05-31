import sys
import webbrowser

from invoke import task


@task
def test(ctx):
    import pytest
    retcode = pytest.main([])
    sys.exit(retcode)


# TODO(dmr, 2017-05-31): dry out readme & contrib
@task
def readme(ctx, browse=True):
    ctx.run('rst2html.py README.rst > /tmp/README.html')
    if browse:
        webbrowser.open_new_tab('/tmp/README.html')


@task
def contrib(ctx, browse=True):
    ctx.run('rst2html.py CONTRIBUTING.rst > /tmp/CONTRIBUTING.html')
    if browse:
        webbrowser.open_new_tab('/tmp/CONTRIBUTING.html')
