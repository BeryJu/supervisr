"""Supervisr UI tasks"""

from invoke import task


@task
def run(context):
    """Run Angular CLI debug server"""
    from django.conf import settings
    with context.cd(settings.BASE_DIR + '/ui'):
        context.run('npm start')

@task
def build(context):
    """Build Angular App with webpack"""
    from django.conf import settings
    with context.cd(settings.BASE_DIR + '/ui'):
        context.run('npm run-script build')

@task
def lint(context):
    """Run TSLint"""
    from django.conf import settings
    with context.cd(settings.BASE_DIR + '/ui'):
        context.run('npx tslint -c tslint.json --project src')
