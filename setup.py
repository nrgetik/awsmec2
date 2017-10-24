#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="awsmec2",
    version="0.1.1",
    description="Tool for managing AWS instances",
    # long_description="",
    url="https://github.com/nrgetik/awsmec2",
    author="Thomas Gordon",
    # license="",
    # keywords="",
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    install_requires=["boto3", "click"]
)
