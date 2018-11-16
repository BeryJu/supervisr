"""Supervisr setup.py"""
import os

from pip._internal.req import parse_requirements
from setuptools import find_packages, setup

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


def read_simple(path, mode='r'):
    """Simple wrapper for file reading"""
    with open(path, mode) as file:
        lines = file.read().split('\n')
        for line in lines:
            if line.startswith('--'):
                lines.remove(line)
        return lines


requirements = parse_requirements('requirements.txt', session='hack')
requirements_dev = parse_requirements('requirements-dev.txt', session='hack')

setup(
    name='supervisr',
    version='0.3.14-alpha',
    description='supervisr your IT.',
    long_description='\n'.join(read_simple('docs/index.md')[2:]),
    long_description_content_type='text/markdown',
    author='BeryJu.org',
    author_email='supervisr@beryju.org',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[str(ir.req) for ir in requirements],
    extras_require={
        'dev': [str(ir.req) for ir in requirements_dev],
    },
    test_suite='supervisr.cli.test_runner.test_runner',
    keywords='supervisr sso server management web hosting dns mail email',
    license='MIT',
    python_requires='>=3.5',
    scripts=['sv'],
    url="https://supervisr.beryju.org/docs/",
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django :: 2.0',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: System :: Clustering',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Networking',
        'Topic :: System :: Systems Administration',
    ],
)
