# Chronograf

!!! warning
    This requires the `supervisr.mod.auth.oauth.provider` module.

Chronograf authentication is supported via OAuth 2. This is integrated into the default Chronograf installation.

```
# /etc/systemd/system/multi-user.target.wants/chronograf.service
[Unit]
Description=Open source monitoring and visualization UI for the entire TICK stack.
Documentation="https://www.influxdata.com/time-series-platform/chronograf/"
After=network-online.target

[Service]
User=chronograf
Group=chronograf
ExecStart=/usr/bin/chronograf --host 0.0.0.0 --port 8888 -b /var/lib/chronograf/chronograf-v1.db -c /usr/share/chronograf/canned
KillMode=control-group
Restart=on-failure
Environment=GENERIC_CLIENT_ID=<client_id>
Environment=GENERIC_CLIENT_SECRET=<client_secret>
Environment=GENERIC_AUTH_URL=https://<supervisr install url>/app/mod/auth/oauth/provider/authorize/
Environment=GENERIC_TOKEN_URL=https://<supervisr install url>/app/mod/auth/oauth/provider/token/
Environment=GENERIC_API_URL=https://<supervisr install url>/api/app/mod/auth/oauth/provider/v1/accounts/me/?format=openid
Environment=PUBLIC_URL=http://<external chronograf URL with port>
Environment=TOKEN_SECRET=supersupersecret
Environment=GENERIC_SCOPES=read
Environment=GENERIC_NAME=supervisr

[Install]
WantedBy=multi-user.target
```