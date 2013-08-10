#!/usr/bin/env python


from setuptools import setup, find_packages

setup(
    name='octotester',
    version='0.01',
    packages=find_packages(),
    test_suite='octotester.tests',
)
