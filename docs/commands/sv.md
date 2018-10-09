# The `sv` command

`sv` is a globally installed command used to interact with supervisr.

When called without any arguments, you will get an output like this:

```
Available tasks:

  dev.init                    Create a new supervisr module
  module.install              Install a supervisr module from Git
  run.migrate                 Apply migrations
  run.ui                      Run Angular CLI debug server
  run.web                     Run CherryPY-based application server
  run.worker                  Run Celery worker
  run.worker-monitor          Run Celery flower
  run.worker-scheduler        Run Celery beat worker
  utils.generate-secret-key   Generate Django SECRET_KEY
```

All these tasks are either used in service definitions or can be used for module development.

!!! notice
    If you install supervisr in a virtualenv, more tasks specific to development will be shown.

You can also use `sv` to interact with Django's `manage.py` by executing `sv manage [...]`. These commands will be passed to Django and will be called within supervisr's virtualenv.
