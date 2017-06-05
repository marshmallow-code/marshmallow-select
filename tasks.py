import sys
import webbrowser

from invoke import task


@task
def test(ctx):
    import pytest
    retcode = pytest.main(['-v'])
    sys.exit(retcode)


@task
def build(ctx):
    ctx.run('python setup.py sdist', echo=True)
    ctx.run('python setup.py bdist_wheel', echo=True)


@task
def publish(ctx):
    clean(ctx)
    build(ctx)
    ctx.run('twine upload dist/*', echo=True)


@task
def clean(ctx):
    ctx.run("rm -rf build")
    ctx.run("rm -rf dist")
    ctx.run("rm -rf marshmallow_select.egg-info")
    print("Cleaned up.")


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


#
# misc tasks
#


@task
def build_sdist(ctx):
    ctx.run('python setup.py sdist', echo=True)


@task
def build_bdist(ctx):
    ctx.run('python setup.py bdist_wheel', echo=True)
