
# External Authentication Sources

## Twitter:

```
name: twitter
request_token_url: https://api.twitter.com/oauth/request_token
authorization_url: https://api.twitter.com/oauth/authenticate
access_token_url: https://api.twitter.com/oauth/access_token
profile_url: https://api.twitter.com/1.1/account/verify_credentials.json
```

## Facebook:

```
name: facebook
authorization_url: https://www.facebook.com/v2.8/dialog/oauth
access_token_url: https://graph.facebook.com/v2.8/oauth/access_token
profile_url: https://graph.facebook.com/v2.8/me?fields=name,email,short_name
```

## GitHub:

```
name: github
authorization_url: https://github.com/login/oauth/authorize
access_token_url: https://github.com/login/oauth/access_token
profile_url: https://api.github.com/user
```

## Discord

```
name: discord
authorization_url: https://discordapp.com/api/oauth2/authorize
access_token_url: https://discordapp.com/api/oauth2/token
profile_url: https://discordapp.com/api/users/@me
```

## Google

```
name: google
authorization_url: https://accounts.google.com/o/oauth2/auth
access_token_url: https://accounts.google.com/o/oauth2/token
profile_url: https://www.googleapis.com/oauth2/v1/userinfo
```
