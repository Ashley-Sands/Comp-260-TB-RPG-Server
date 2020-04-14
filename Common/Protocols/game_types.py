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
GA_END_TURN          = 2
GA_END_GAME        = 3

# A
def game_Action( from_client_name, player_id, action ):
    return locals()


# E
def explosion( from_client_name, x, y, z ):
    return locals()


# D
def apply_damage( from_client_name, player_id, health, kill ):
    return locals()


# R
def look_at( from_client_name, player_id, x, y, z ):
    return locals()


# B
def build_object( from_client_name, player_id, type, obj_id ):
    return locals()

# Game loop actions
GL_CHANGE = 0
GL_START = 1
GL_END = 2

# >
def game_loop( from_client_name, player_id, action, t ):
    return locals()


# +
def relic_count ( from_client_name, player_id, count ):
    return locals()


# Server Object types
SO_PLAYER = 0
SO_RELIC = 1
SO_BLOCK = 2
SO_RELIC_AREA = 3

# server object action types
SOA_DEFAULT = 0
SOA_ADD = 1
SOA_REMOVE = 2


# # (as in its id is hash)
def server_object( from_client_name, type, object_id, x, y, z, action=SOA_DEFAULT ):
    return locals()
