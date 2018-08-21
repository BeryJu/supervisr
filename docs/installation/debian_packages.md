# Installation of Supervisr


#### Add the repo Key

```
wget -O - -q https://apt.beryju.org/public.key | apt-key add -
```

#### Add the repo with your API Key

```
deb https://supervisr.beryju.org/deb/ stable supervisr
```

#### Install package

```
apt update
apt install mysql-server supervisr
```

!!! info
    If you already have MySQL setup, or plan on using a separate MySQL Server, install supervisr using `apt install supervisr`

