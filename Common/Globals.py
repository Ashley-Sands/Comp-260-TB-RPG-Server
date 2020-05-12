import socket
import os

class Global:

    DEBUG = False


class GlobalConfig:

    __CONFIG__ = {}

    @staticmethod
    def get(config_name):
        """Gets the config data for name"""
        if config_name.lower() in GlobalConfig.__CONFIG__:
            return GlobalConfig.__CONFIG__[config_name.lower()]

    @staticmethod
    def set(config_name, data):
        """Sets or adds (if not exist) to the global config"""
        GlobalConfig.__CONFIG__[config_name.lower()] = data

    @staticmethod
    def is_set(config_name):
        return config_name in GlobalConfig.__CONFIG__

def setup( config_module ):

    """
    :param config: dict key, config name, value, config value
    :return:
    """

    config = config_module.conf

    for c in config:
        GlobalConfig.set( c, config[c] )

