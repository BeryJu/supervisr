"""Supervisr setup.py"""
import os

from setuptools import find_packages, setup

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
    version='0.3.2-alpha',
    description='supervisr your IT.',
    long_description='\n'.join(read_simple('README.md')),
    author='BeryJu.org',
    author_email='supervisr@beryju.org',
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_simple('requirements.txt'),
    extras_require={
        'dev': read_simple('requirements-dev.txt'),
    },
    test_suite='supervisr.cli.test_runner.test_runner',
    keywords='supervisr sso server management web hosting dns mail email',
    license='MIT',
    classifiers=[
        'Development Status:: 3 - Alpha',
        'Framework :: Django :: 2.0',
        'Intended Audience :: System Administrators',
        'License :: MIT',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: System :: Clustering',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Networking',
        'Topic:: System:: Systems Administration',
    ],
    python_requires='>=3.5',
    scripts=['scripts/supervisr-ctl'],
    url="https://supervisr.beryju.org/docs/",
    zip_safe=False,
)
