import Common.DEBUG as DEBUG
import Common.database as db
import Sockets.ServerLobbySocket as ServerLobbySocket
import Sockets.SocketHandler as SocketHandler
import Common.constants as const
import Common.message as message
import time
import os
import Common.Globals as Global
config = Global.GlobalConfig

LOBBY_UPDATE_CLIENT_INTERVALS = 30  # seconds
LOBBY_UPDATE_INTERVALS = 1  # seconds
MIN_LOBBY_COUNT = 2

def procrcess_connection( conn ):

    if not conn.get_client_key()[1].strip():
        DEBUG.LOGS.print( "Unable to process client, not set up", conn.get_client_key(), message_type=DEBUG.LOGS.MSG_TYPE_WARNING )
        return

    if time.time() > conn.next_update_time:
        # send the client a list of lobbies available to join
        current_lobby_count = database.available_lobby_count()

        if current_lobby_count < MIN_LOBBY_COUNT:
            database.add_new_lobby()

        lobbies, lobb_curr_players = database.select_all_available_lobbies()
        lobb_names = []
        lobb_id = []
        lobb_max_clients = []

        # organize the lobby data
        for lobb in lobbies:
            lobb_id.append( lobb[0] )
            lobb_names.append( lobb[1] )
            lobb_max_clients.append( lobb[3] )

        conn.next_update_time = time.time() + LOBBY_UPDATE_CLIENT_INTERVALS

        lobby_message = message.Message("l")
        lobby_message.new_message( const.SERVER_NAME, lobb_names, lobb_id,
                                   lobb_curr_players, lobb_max_clients )

        conn.send_message(lobby_message)


def process_client_identity( message_obj ):

    DEBUG.LOGS.print("Recivedd id", message_obj["client_id"], message_obj["reg_key"] )
    from_conn = message_obj.from_connection
    # add the clients data to the connection
    from_conn.set_client_key( message_obj["client_id"], message_obj["reg_key"] )
    from_conn.client_nickname = message_obj["nickname"]

if __name__ == "__main__":

    running = True

    # set up
    Global.setup()

    DEBUG.LOGS.init()
    DEBUG.LOGS.set_log_to_file(message=True, warning=True, error=True, fatal=True)

    database = db.Database()

    # bind message functions
    message.Message.bind_action( "i", process_client_identity )

    port = config.get( "internal_port" )

    # setup socket and bind to accept client socket
    socket_handler = SocketHandler.SocketHandler( config.get( "internal_host_lobbies" ), port,
                                                  15, ServerLobbySocket.ServerLobbySocket )

    socket_handler.start()

    # Welcome the server
    DEBUG.LOGS.print("Welcome",config.get("internal_host_lobbies"), ":", config.get("internal_port") )

    while running:
        # lets keep it clean :)
        socket_handler.process_connections( procrcess_connection )
        time.sleep(0.5)