import Common.DEBUG as DEBUG
import Common.database as db
import Sockets.ServerLobbySocket as ServerLobbySocket
import Sockets.SocketHandler as SocketHandler
import Common.constants as const
import Common.message as message
import time
import Common.Protocols.status as statusProtocols
import Common.actions as actions
import os
import Common.Globals as Global
config = Global.GlobalConfig

LOBBY_UPDATE_CLIENT_INTERVALS = 5  # seconds
LOBBY_UPDATE_INTERVALS = 1  # seconds
MIN_LOBBY_COUNT = 2

def procrcess_connection( conn ):


    # process any messages from the client
    while conn.receive_message_pending():
        conn.receive_message().run_action()

    if not conn.get_client_key()[1].strip():
        DEBUG.LOGS.print( "Unable to process client, not set up", conn.get_client_key(), message_type=DEBUG.LOGS.MSG_TYPE_WARNING )
        conn.safe_close()
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
            lobb_names.append( lobb[2] )
            lobb_max_clients.append( lobb[4] )

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

def process_join_lobby( message_obj ):

    from_conn = message_obj.from_connection

    # check there is space for the client in the lobby
    # if so register them in :)
    status, err_msg = database.join_lobby( from_conn.get_client_key()[0], message_obj["lobby_id"] )

    if status:
        # change scene
        response_message = message.Message('s')
        response_message.new_message(const.SERVER_NAME, const.SCENE_NAMES["Lobby"])
    else:
        # send error status
        response_message = message.Message('!')
        response_message.new_message(const.SERVER_NAME, statusProtocols.SS_LOBBY_REQUEST, False, err_msg)
        pass

    # send the response and disconnect if we have joined
    from_conn.send_message( response_message )

    if status:
        from_conn.safe_close()

if __name__ == "__main__":

    running = True

    # set up
    Global.setup()

    DEBUG.LOGS.init()
    DEBUG.LOGS.set_log_to_file(message=True, warning=True, error=True, fatal=True)

    database = db.Database()

    # bind message functions
    message.Message.bind_action( 'i', process_client_identity )
    message.Message.bind_action( 'L', process_join_lobby )

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
