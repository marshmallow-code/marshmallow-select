from setuptools import setup, find_packages

# NOTE(dmr, 2017-05-03): These are the versions I've actually used it
# with; no idea what actual requirements are.
REQUIRES = (
    'marshmallow>=2.10.3',
    'SQLAlchemy>=1.1.6',
)

setup(
    name='marshmallow-select',
    packages=find_packages(),
    description='make sqlalchemy select fields with marshmallow schemas',
    version='1.0.4',
    install_requires=REQUIRES,
    author='dmr',
    author_email='dradetsky@gmail.com',
    url='https://github.com/marshmallow-code/marshmallow-select',
    license='WTFPL',
    keywords=('marshmallow', 'sqlalchemy'),
    # NOTE(dmr, 2017-05-03): I assume/hope versions 3.{4,5} work. I've only used 6.
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        # NOTE(dmr, 2017-05-25): It's FSF approved, not explicitly
        # DFSG-disapproved, and Debian includes Windowmaker, so I
        # _assume_. Anyway, if I'm wrong it's DFSG's fault for not
        # being more explicit.
        'License :: DFSG approved',
        'License :: Freely Distributable',
        'License :: Public Domain',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Database',
    ],
    test_suite='tests',
)
