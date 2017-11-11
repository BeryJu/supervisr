# OAuth 2

## OAuth 2 endpoint URLs

Authorize: `https://<installation URL>/app/mod/auth/oauth/provider/authorize//`

Token: `https://<installation URL>/app/mod/auth/oauth/provider/token/`

## API calls

API calls should be made with a `Authorization: Bearer` Header, which contains your access token.

For example:

```
curl -X GET \
     -H "Authorization: Bearer your_api_token" \
     "https://<installation URL>/api/core/v1/account/me/?type=openid"
```

...which would return...

```
{
    'id': 1,
    'pk': 1,
    'first_name': 'System User',
    'email': 'root@localhost',
}
```
