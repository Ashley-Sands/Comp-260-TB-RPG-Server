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

def setup():

    # global connections (ie online)
    if os.name == 'nt':  # local testing
        GlobalConfig.set("host", "localhost_0")
    else:  # docker production setup
        GlobalConfig.set("host", "0.0.0.0")         # allow connections from the outside world

    GlobalConfig.set("port", 8222)

    # fixed local connections (all use the internal port, 8223)
    GlobalConfig.set( "internal_host_auth", "localhost_auth" )
    GlobalConfig.set( "internal_host_lobbies", "localhost_lobbies" )

    # dynamic local connections
    GlobalConfig.set("internal_host", socket.gethostname())     # internal host address
    GlobalConfig.set("internal_port", 8223)                     # internal port

    # MYSQL connection (local)
    GlobalConfig.set("mysql_host", "localhost_sql")
    GlobalConfig.set("mysql_user", "root")
    GlobalConfig.set("mysql_pass", "password!2E")
