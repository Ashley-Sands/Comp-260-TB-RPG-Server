# the functions used to enforce the message types
# Request types are like identity request ect...
# every think must contain a from client name

# See Protocol list for details


# i
def identity_request( from_client_name, client_id, nickname, reg_key ):
    return locals()


# I
def identity_status( from_client_name, client_id, reg_key, ok ):
    return locals()


# L
def join_lobby_request( from_client_name, scene_id ):
    return locals()