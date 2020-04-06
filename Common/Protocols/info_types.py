# the functions used to enforce the message types
# info types are things like lobby and player list ect...
# every think must contain a from client name

# See Protocol list for details


# l
def lobby_list( from_client_name, lobby_names, lobby_ids, current_clients, max_clients ):
    return locals()


# C
def lobby_client_list( from_client_name, client_ids, client_nicknames ):
    return locals()


# L
def lobby_info( from_client_name, level_name, min_players, max_players, starts_in ):
    return locals()


# G
def game_client_list( from_client_name, client_ids, client_nicknames, client_player_ids ):
    return locals()

