import socket

# config to run all servers as containers in a single docker instance
# config files must contain the var conf as a dict.

conf = {
    # inbound connections, from the outside world :)
    "host": "0.0.0.0",
    "port": 8222,

    # dynamic host addresses for local connections
    "internal_host": socket.gethostname(),
    "internal_port": 8223,

    # fixed host, local connections
    "internal_host_auth": "localhost_auth",
    "internal_host_lobbies": "localhost_lobbies",

    # mysql
    "mysql_host": "localhost",
    "mysql_user": "root",
    "mysql_pass": "password!2E"

}
