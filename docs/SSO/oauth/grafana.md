# Grafana

!!! warning
    This requires the `supervisr.mod.auth.oauth.provider` module.

Grafana authentication is supported via OAuth 2. This is integrated into the default Grafana installation.

```ini
# /etc/grafana/grafana.ini
##################### Grafana Configuration Example #####################

#################################### Generic OAuth ##########################
[auth.generic_oauth]
enabled = true
name = supervisr
allow_sign_up = true
client_id = <client_id>
client_secret = <client_secret>
scopes = read
auth_url = https://<supervisr install url>/app/mod/auth/oauth/provider/authorize/
token_url = https://<supervisr install url>/app/mod/auth/oauth/provider/token/
api_url = https://<supervisr install url>/api/app/mod/auth/oauth/provider/v1/accounts/me/?format=openid
```