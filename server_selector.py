import Common.DEBUG as DEBUG
import Common.database as db
import Common.message as message
import Sockets.ServerSelectSocket as ServerSelectSocket
import Sockets.SocketHandler as SocketHandler
import time
import Common.constants as const
import Common.Globals as Global
config = Global.GlobalConfig

def cleanup_connections( conn ):

    # remove the client from the database
    database.remove_client( conn.get_client_key()[1] )

def get_host( conn, send_scene_change=False ):
    """
        Gets the host and connection type
    :param conn:                the connection of the target host that we want
    :param send_scene_change:   if theres a scene change should we send the message
    :return:                    tuple ( connection type, host )
    """

    # *** IMPORTANT ***
    # 1. if the user does not have an auth key set on the (selector) server the user must get authorized.
    #    either by sending the auth key to the server to be verified or failing that the auth server
    #    will assign a new key
    # 2. Once the user has been authorized
    #    A.     If no lobby is set on the user in the database they are sent to the lobbies server
    #    B.     If a lobby is set the users is sent to the lobby
    #    C.     If a lobby and game is set, the users is still be sent to lobby, this singles that the
    #            game is ready to launch when the lobby period is complete.
    #    D.     If no lobby is set but a game is, the users is sent to the game.
    #
    #   So to summarize:
    #   Auth trumps all, lobby trumps game, and game trumps lobbies.
    #   Even briefer
    #   Auth->lobby->game->lobbies
    #

    # find the players current state
    if not conn.get_client_key()[ 1 ].strip():
        # if there is no reg key the user needs to be authed into the system
        # so we can determin what to do with them
        conn.conn_mode( conn.CONN_TYPE_AUTH )
        return conn.CONN_TYPE_AUTH, config.get( "internal_host_auth" )
    else:
        # get the clients data.
        reg_key = conn.get_client_key()[1]
        current_client_lobby = database.get_client_lobby( reg_key )

        if current_client_lobby > -1:
            # if a lobby has been assigned to the client
            # are they in the lobby or game state

            lobby_host_id, game_host_id = database.get_lobby_host_ids(current_client_lobby)
            connect_to_host = -1

            if lobby_host_id > -1:
                # off to the lobbies
                connect_to_host = database.get_lobby_host( lobby_host_id )
                send_scene_change_message( send_scene_change, conn, const.SCENE_NAMES[ "Lobby" ] )
            elif game_host_id > -1:
                # off to the game
                connect_to_host = database.get_game_host( game_host_id )
                scene_name = database.get_lobby_target_scene_name( current_client_lobby )
                send_scene_change_message( send_scene_change, conn, scene_name )
            else:
                DEBUG.LOGS.print( "No lobby host or game host assigned to lobby", current_client_lobby,
                                  message_type=DEBUG.LOGS.MSG_TYPE_FATAL )

            return conn.CONN_TYPE_DEFAULT, connect_to_host

        else:  # send the client off to the lobbies host
            send_scene_change_message( send_scene_change, conn, const.SCENE_NAMES["LobbyList"] )
            return conn.CONN_TYPE_DEFAULT, config.get( "internal_host_lobbies" )


def send_scene_change_message( send_message, conn, scene_name ):

    if send_message:
        scene_message = message.Message('s')
        scene_message.new_message(const.SERVER_NAME, scene_name)
        conn.send_message(scene_message)


def client_connection_accepted ( conn, addr ):
    DEBUG.LOGS.print( "Client joined", addr )
    conn.connect_passthrough( *get_host( conn, True ), 8223 )

def process_connections( conn ):

    if not conn.passthrough_mode():
        conn.connect_passthrough( *get_host( conn, True ), 8223 )
        pass

if __name__ == "__main__":

    running = True

    Global.setup()

    DEBUG.LOGS.init()
    DEBUG.LOGS.set_log_to_file(message=True, warning=True, error=True)

    database = db.Database()

    # wait for db to connection
    while not database.database.test_connection():
        time.sleep(10) # seconds

    socket_handler = SocketHandler.SocketHandler( config.get("host"), config.get("port"),
                                                  15, ServerSelectSocket.ServerSelectSocket)

    # bind our actions onto the connection / protocol callbacks
    socket_handler.accepted_client_bind( client_connection_accepted )

    # Welcome the server
    DEBUG.LOGS.print("Welcome",config.get("host"), ":", config.get("port") )

    socket_handler.start()

    while running:

        # clean up any zombie sockets
        socket_handler.process_connections( process_func=process_connections, extend_remove_connection_func=cleanup_connections )

        # reconnect any passthrough sockets that have become disconnected
        # this usually happens when the client is no longer welcome on the server
        # ie, when the game has ended, or game is starting, joining lobbies ect...
        pass