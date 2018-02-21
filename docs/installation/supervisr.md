# Installation of Supervisr

## Closed beta installation

!!! warning
    These steps only apply to the closed beta. To check if you have access to the beta, check [here](https://my.beryju.org/products/supervisr-closed-beta/). To request access, fill out [this](https://docs.google.com/forms/d/e/1FAIpQLSfwh9xcnl_a8banbWazusnLVUA3YSb-TC_4aWizec3TEmkgOg/viewform?usp=sf_link) form.

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

