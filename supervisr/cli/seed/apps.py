"""Supervisr module seed app config"""

from supervisr.core.apps import SupervisrAppConfig


class SupervisrModSeedConfig(SupervisrAppConfig):
    """Supervisr module seed app config"""

    name = 'supervisr_seed'
    label = 'supervisr_seed'
