# OAuth 2

## OAuth 2 endpoint URLs

Authorize: `https://my.beryju.org/api/oauth2/authorize/`

Token: `https://my.beryju.org/api/oauth2/token/`

## API calls

API calls should be made with a `Authorization: Bearer` Header, which contains your access token.

For example:

```
curl -X GET \
     -H "Authorization: Bearer your_api_token" \
     "https://my.beryju.org/api/r2/account/me?type=json"
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
