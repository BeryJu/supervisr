"""Supervisr setup.py"""
import os

from setuptools import find_packages, setup

from supervisr import __version__

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

def read_simple(path, mode='r'):
    """Simple wrapper for file reading"""
    with open(path, mode) as file:
        lines = file.read().split('\n')
        for line in lines:
            if line.startswith('-e'):
                lines.remove(line)
        return lines

setup(
    name='supervisr',
    version=__version__,
    description='supervisr your IT.',
    author='BeryJu.org',
    author_email='supervisr@beryju.org',
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_simple('requirements.txt'),
    extras_require={
        'dev': read_simple('requirements-dev.txt'),
    },
    scripts=['manage.py'],
    url="https://supervisr.beryju.org/docs/",
)
