# Installation of Supervisr 

### Install all packages

```
apt install git python3 python3-pip libmysqlclient-dev
pip3 install virtualenv invoke
```

### Option A: Download a packaged release

```
wget https://dl.supervi.sr/latest.tgz
tar xvzf latest.tgz
```

### Option B: Checkout the source

```
git clone https://git.beryju.org/BeryJu.org/supervisr.git
```

### Clone Repo, create virtualenv and install the rest

```
cd supervisr/
virtualenv env/
source env/bin/activate
pip install invoke
inv install
```
