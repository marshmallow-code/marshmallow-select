from setuptools import setup

# NOTE(dmr, 2017-05-03): These are the versions I've actually used it
# with; no idea what actual requirements are.
REQUIRES = (
    'marshmallow>=2.10.3',
    'SQLAlchemy>=1.1.6',
)

setup(
    name='marshmallow-select',
    package='marshmallow_select',
    description='make sqlalchemy select fields with marshmallow schemas',
    version='1.0.1',
    install_requires=REQUIRES,
    author='dmr',
    author_email='dmr@distribute.com',
    url='https://github.com/Distributd/marshmallow-select',
    # NOTE(dmr, 2017-05-03): I assume/hope versions 3.{4,5} work. I've only used 6.
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

)
