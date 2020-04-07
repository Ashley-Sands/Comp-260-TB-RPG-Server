# the functions used to enforce the message types
# any type of action that happens with in the game
# every think must contain a from client name

# See Protocol list for details


def move_player( from_client_name, x, y, z ):
    return locals()

# Server Object types
SO_PLAYER = 0
SO_RELIC = 1

def server_object( from_client_name, type, object_id, x, y, z ):
    return locals()
