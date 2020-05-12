import socket
import Configs.secrets as secrets

# config to run all servers as containers in a single docker instance
# config files must contain the var conf as a dict.

host_name = socket.gethostname()
ip = socket.gethostbyname( host_name )

secrets.Secrets.load()

conf = {

    # inbound connections, from the outside world :)
    "host": "0.0.0.0",
    "port": 8222,

    # dynamic host addresses for local connections
    "internal_host": ip,
    "internal_port": 8223,

    # fixed host, local connections
    "internal_host_auth": "localhost_auth",
    "internal_host_lobbies": "localhost_lobbies",

    # mysql
    "mysql_host": secrets.Secrets.store["sql_host"],
    "mysql_user": secrets.Secrets.store["sql_user"],
    "mysql_pass": secrets.Secrets.store["sql_password"]

}
