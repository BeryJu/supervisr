# Error Reporting

To comply with the GDPR, error-reporting is disabled by default. To enable it, you can set the following setting in your `config.py` (Debian) or `local_settings.py` (Source) file:

```python
SENTRY_DSN = ('https://c5f3fa4e642d4dbfaa5db684bd0f6a13:7d639a81f'
              '45e44e39713fd4d2c680e19@sentry.services.beryju.org/6')
```

This will automatically send errors to `sentry.services.beryju.org`. The Data includes servername, client IP address, signed in username and browser information.

You can also use this variable to send errors to your own Sentry install.
