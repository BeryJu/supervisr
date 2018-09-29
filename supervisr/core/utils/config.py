"""supervisr core config loader"""
import os
from contextlib import contextmanager
from glob import glob
from logging import getLogger
from typing import Any

import yaml
from django.conf import ImproperlyConfigured

SEARCH_PATHS = [
    'supervisr/environments/default.yml',
    '/etc/supervisr/config.yml',
] + glob('/etc/supervisr/config.d/*.yml', recursive=True) + [
    'supervisr/environments/',
]
LOGGER = getLogger(__name__)
ENVIRONMENT = os.getenv('SUPERVISR_ENV', 'local')

class ConfigLoader:
    """Search through SEARCH_PATHS and load configuration"""

    __config = {}
    __context_default = None
    __sub_dicts = []

    def __init__(self):
        super().__init__()
        base_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), '../../..'))
        for path in SEARCH_PATHS:
            # Check if path is relative, and if so join with base_dir
            if not os.path.isabs(path):
                path = os.path.join(base_dir, path)
            if os.path.isfile(path) and os.path.exists(path):
                # Path is an existing file, so we just read it and update our config with it
                self.update_from_file(path)
            elif os.path.isdir(path) and os.path.exists(path):
                # Path is an existing dir, so we try to read the env config from it
                env_path = os.path.join(path, ENVIRONMENT+'.yml')
                if os.path.isfile(env_path) and os.path.exists(env_path):
                    # Update config with env file
                    self.update_from_file(env_path)

    def handle_secret_key(self):
        """Handle `secret_key_file`"""
        if 'secret_key_file' in self.__config:
            secret_key_file = self.__config.get('secret_key_file')
            if os.path.isfile(secret_key_file) and os.path.exists(secret_key_file):
                with open(secret_key_file) as file:
                    self.__config['secret_key'] = file.read()

    def update_from_file(self, path: str):
        """Update config from file contents"""
        with open(path) as file:
            try:
                self.__config.update(yaml.safe_load(file))
            except yaml.YAMLError as exc:
                raise ImproperlyConfigured from exc

    def update_from_dict(self, update: dict):
        """Update config from dict"""
        self.__config.update(update)

    @contextmanager
    def default(self, value: Any):
        """Contextmanage that sets default"""
        self.__context_default = value
        yield
        self.__context_default = None

    @contextmanager
    # pylint: disable=invalid-name
    def cd(self, sub: str):
        """Contextmanager that descends into sub-dict. Can be chained."""
        self.__sub_dicts.append(sub)
        yield
        self.__sub_dicts.pop()

    def get(self, key: str, default=None) -> Any:
        """Get value from loaded config file"""
        if default is None:
            default = self.__context_default
        config_copy = self.__config
        for sub in self.__sub_dicts:
            config_copy = config_copy.get(sub, None)
        return config_copy.get(key, default)

    @property
    def raw(self) -> dict:
        """Get raw config dictionary"""
        return self.__config


CONFIG = ConfigLoader()
