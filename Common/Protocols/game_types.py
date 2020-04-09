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


# Game Action Types
GA_DROP_ITEM         = 0
GA_LAUNCH_PROJECTILE = 1


# A
def game_Action( from_client_name, player_id, action ):
    return locals()


# E
def explosion( from_client_id, x, y, z ):
    return locals()


# D
def apply_damage( from_client_id, player_id, damage, kill ):
    return locals()


# R # todo: remove
def Look_At( from_client_name, player_id, x, y, z ):
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
