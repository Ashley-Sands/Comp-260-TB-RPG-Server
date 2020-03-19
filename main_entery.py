from common.socket import SocketConnection, SocketClient
from common.database import Database
import message
import constants
import time
import DEBUG

MAX_FREE_LOBBIES = 3

# The entry server is responsable for registering the player into the network
# and send each client a list of available games every now and then

def accepted_client( connection ):
    # request the player identity. (this needs to be done in entry)
    identity = message.Message( constants.SERVER_NAME, 'i' )
    identity.message = identity.new_message( constants.SERVER_NAME, "", "" )

    connection.send_message(identity)

def get_lobby_message( ):

    if database.available_lobby_count() <= MAX_FREE_LOBBIES:
        database.add_new_lobby()

    lobbies, current_players = database.select_all_available_lobbies()

    # sort the data into individual list

    lobby_ids = []
    level_names = []
    min_players = []
    max_players = []

    for l in lobbies:
        lobby_ids.append(l[0])
        level_names.append(l[2])
        min_players.append(l[3])
        max_players.append(l[4])

    game_list = message.Message(constants.SERVER_NAME, 'g')
    game_list.message = game_list.new_message(constants.SERVER_NAME, lobby_ids, level_names,
                                              min_players, max_players, current_players)

    return game_list;

if __name__ == "__main__":

    running = True
    update_lobby_list_intervals = 15
    next_lobby_update = 0

    DEBUG.DEBUG.init()
    database = Database()   # TODO: Setup config.

    active_socket = SocketConnection("127.0.0.1", 8222, 20, SocketClient)
    active_socket.accepted_client_bind( accepted_client )

    message.Message.initialize_actions( database, active_socket.send_message,
                                        active_socket.get_client_keys, active_socket.get_connection )

    active_socket.start()

    # Process each client
    while running:
        # check that all clients are valid
        # and if its time update there lobby list

        # we must get the keys from the dict otherwise its get resized during iteration **crash** :D
        socks = list(active_socket.connections)

        for sock in socks:
            if not active_socket.connections[sock].valid():
                # remove the client
                continue

            try:
                while active_socket.connections[sock].receive_message_pending():
                    msg = active_socket.connections[sock].receive_message()
                    msg.run_action()
            except Exception as e:
                DEBUG.DEBUG.print("Can not process message", e, message_type=DEBUG.DEBUG.MESSAGE_TYPE_ERROR)

            # TODO: move to thread??
            if time.time() > next_lobby_update and active_socket.connections[sock].registered:
                # send lobby update to all clients
                game_list = get_lobby_message()
                active_socket.connections[sock].send_message(game_list)
                active_socket.remove_connection( sock )


        if time.time() > next_lobby_update:
            next_lobby_update = time.time() + update_lobby_list_intervals
