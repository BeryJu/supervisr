# Installing the Bacula Module

Simply run

```
supervisr-ctl mod.install https://git.beryju.org/BeryJu.org/supervisr_mod_contrib_bacula.git
supervisr-ctl utils.migrate
systemctl restart supervisr
```

After the restart you can see a `Bacula` entry in the Admin category. In there you can set the DB connection details.