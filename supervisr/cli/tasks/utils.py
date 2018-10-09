"""Supervisr Invoke Tasks"""
from random import SystemRandom

from invoke import task


@task
# pylint: disable=unused-argument
def generate_secret_key(ctx):
    """Generate Django SECRET_KEY"""
    charset = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"
    print(''.join([SystemRandom().choice(charset) for i in range(50)]))
