# Creating a module

Modules simly are a django application within the `supervisr/mod/` directory. These can either be created by using `django-admin` or copying the `_seed` folder. This foler contains an empty django application, which already makes use of all the supervisr helpers.

## Loading a module

Loading a module is done as usual in a django application. The full module path to the `AppConfig` should be appended to the `local_settings` file.
