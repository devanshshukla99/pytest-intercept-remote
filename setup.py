#!/usr/bin/env python

from setuptools import setup

setup(
    name="pytest-intercept",
    packages=['pytest-intercept']
    entry_points={
        'pytest11': [ 'pytest_intercept = pytest_intercept.plugin',
        ]},
    # custom PyPI classifier for pytest plugins
    classifiers=[
        "Framework :: Pytest",
    ],
)