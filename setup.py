#!/usr/bin/env python
import os
from setuptools import setup

def read(filen):
    with open(os.path.join(os.path.dirname(__file__), filen), "r") as fp:
        return fp.read()
 
setup (
    name = "jump",
    version = "0.1",
    description="a JSON-based messaging and presence protocol",
    long_description=read("README.md"),
    author="Alec Elton",
    author_email="alec.elton@gmail.com", # Removed to limit spam harvesting.
    url="http://github.com/basementcat/jump",
    packages=["jump", "tests"],
    test_suite="nose.collector",
    install_requires=['secure-smtpd', 'argparse'],
    tests_require=["nose"]
)