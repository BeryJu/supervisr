"""
Supervisr Stats Graphite AppConfig
"""


from supervisr.core.apps import SupervisrAppConfig


class SupervisrModStatGraphiteConfig(SupervisrAppConfig):
    """
    Supervisr TFA AppConfig
    """

    name = 'supervisr.mod.stats.graphite'
