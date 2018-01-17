"""Supervisr setup.py"""
import os
from setuptools import setup, find_packages

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

def read_simple(path, mode='r'):
    """Simple wrapper for file reading"""
    with open(path, mode) as file:
        return file.read()

setup(
    name='supervisr',
    version='0.1dev',
    description='supervisr your IT.',
    author='BeryJu.org',
    author_email='supervisr@beryju.org',
    packages=find_packages(),
    install_requires=read_simple('requirements.txt').split('\n'),
    scripts=['manage.py'],
    url="https://supervisr.beryju.org/docs/",
)
