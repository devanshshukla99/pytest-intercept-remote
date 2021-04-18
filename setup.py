#!/usr/bin/env python

# import os
# from setuptools import setup

# setup(use_scm_version={'write_to': os.path.join('pytest_intercept', 'version.py')})

# sample ./setup.py file
from setuptools import setup

setup(
    name="pytest-intercept",
    packages=['pytest-intercept']
    entry_points={
        'pytest11': [
            'pytest_intercept = pytest_intercept.plugin',
        ]
    },
    # custom PyPI classifier for pytest plugins
    classifiers=[
        "Framework :: Pytest",
    ],
)