# Installation of Supervisr 

## Closed beta installation 

#### Add the repo Key

```
wget -O - -q https://apt.beryju.org/public.key | apt-key add -
```

#### Add the repo with your API Key

```
deb https://<api key>@supervisr.beryju.org/apt.php?p= beta supervisr
```

#### Install package

```
apt update
apt install supervisr
```

