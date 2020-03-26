import Common.DEBUG as DEBUG
import Common.database as db
import Common.message as message
import Sockets.ServerSelectSocket as ServerSelectSocket
import Sockets.SocketHandler as SocketHandler
import time
import Common.constants as const
import Common.Globals as Global
config = Global.GlobalConfig


def get_host( conn, send_scene_change=False ):
    """
        Gets the host and connection type
    :param conn:                the connection of the target host that we want
    :param send_scene_change:   if theres a scene change should we send the message
    :return:                    tuple ( connection type, host )
    """

    # find the players current state
    if not conn.get_client_key()[ 1 ].strip():
        # if there is no reg key the user needs to be authed into the system
        # so we can determin what to do with them
        conn.conn_mode( conn.CONN_TYPE_AUTH )
        return conn.CONN_TYPE_AUTH, config.get( "internal_host_auth" )
    else:
        # get the clients data.
        reg_key = conn.get_client_key()[1]
        current_lobby = database.get_client_lobby( reg_key )

        if current_lobby > -1:
            send_scene_change_message( send_scene_change, conn, const.SCENE_NAMES[ "Lobby" ] )
            host = database.get_lobby_host( current_lobby )
            if host is None:
                DEBUG.LOGS.print( "Could not find host", host, "curr lobby", current_lobby, message_type=DEBUG.LOGS.MSG_TYPE_FATAL )
                return -1, None
            else:
                return conn.CONN_TYPE_DEFAULT, host
        else:
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
        time.sleep(5) # try every 5 seconds

    socket_handler = SocketHandler.SocketHandler( config.get("host"), config.get("port"),
                                                  15, ServerSelectSocket.ServerSelectSocket)

    # bind our actions onto the connection / protocol callbacks
    socket_handler.accepted_client_bind( client_connection_accepted )

    # Welcome the server
    DEBUG.LOGS.print("Welcome",config.get("host"), ":", config.get("port") )

    socket_handler.start()

    while running:

        # clean up any zombie sockets
        socket_handler.process_connections( process_connections )

        # reconnect any passthrough sockets that have become disconnected
        # this usually happens when the client is no longer welcome on the server
        # ie, when the game has ended, or game is starting, joining lobbies ect...
        pass