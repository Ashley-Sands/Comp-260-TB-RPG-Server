# the functions used to enforce the message types
# any status types ect...
# every think must contain a from client name

# See Protocol list for details

# server status types
SS_SERVER            = 0
SS_LOBBY_REQUEST     = 1

def server_status(from_client_name, status_type, ok, message):
    return locals()
