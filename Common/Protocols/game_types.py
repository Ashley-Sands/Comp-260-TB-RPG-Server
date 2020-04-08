# the functions used to enforce the message types
# any type of action that happens with in the game
# every think must contain a from client name

# See Protocol list for details


# S
def move_player( from_client_name, x, y, z ):
    return locals()


# P
def collect_item( from_client_name, player_id, object_id ):
    return locals()


# p
def drop_item( from_client_name, player_id ):
    return locals()

# Server Object types
SO_PLAYER = 0
SO_RELIC = 1

# server object action types
SOA_DEFAULT = 0
SOA_ADD = 1
SOA_REMOVE = 0

# # (as in its id is hash)
def server_object( from_client_name, type, object_id, x, y, z, action=SOA_DEFAULT ):
    return locals()
