# Sentry

!!! warning
    This requires the `supervisr.auth.oauth.provider` module.

## Installation

```
# Activate Virtualenv
source virtualenv/bin/activate
# Uninstall any existing versions
pip uninstall sentry-auth-supervisr -y
# Install from git
pip install git+https://git.beryju.org/BeryJu.org/sentry-auth-supervisr.git
```

## Configuration

Set the following settings in `sentry.conf.py`.

```
SUPERVISR_APP_ID = "<client_id>"
SUPERVISR_API_SECRET = "<client_secret>"
```

You can also set `SUPERVISR_BASE_DOMAIN` to the supervisr installation URL if you want to authenticate against your own install. Default is `my.beryju.org`.
