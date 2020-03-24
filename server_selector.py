import Common.DEBUG as DEBUG
import Common.database as db
import Sockets.ServerSelectSocket as ServerSelectSocket
import Sockets.SocketHandler as SocketHandler
import time

import Common.Globals as Global
config = Global.GlobalConfig


def get_host( conn ):
    """
        Gets the host and connect type
    :param conn:    the connection of the target host that we want
    :return:        tuple ( connection type, host )
    """

    # find the players current state
    if not conn.get_client_key()[ 1 ].strip():
        # if there is no reg key the user needs to be authed into the system
        # so we can determin what to do with them
        conn.conn_mode( conn.CONN_TYPE_AUTH )
        return conn.CONN_TYPE_AUTH, config.get( "internal_host_auth" )
    else:
        return -1, ""

def client_connection_accepted ( conn, addr ):
    DEBUG.LOGS.print( "Client joined", addr )
    conn.connect_passthrough( *get_host( conn ), 8223 )

def process_connections( conn ):
    if not conn.passthrough_mode():
        conn.connect_passthrough( *get_host( conn ), 8223 )
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
        time.sleep(0.5)

        # reconnect any passthrough sockets that have become disconnected
        # this usually happens when the client is no longer welcome on the server
        # ie, when the game has ended, or game is starting, joining lobbies ect...
        pass