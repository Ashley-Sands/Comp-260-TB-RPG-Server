import Common.DEBUG as DEBUG
import Common.database as db
import Sockets.ServerSelectSocket as ServerSelectSocket
import Sockets.SocketHandler as SocketHandler
import time

import Common.Globals as Global
config = Global.GlobalConfig

def client_connection_accepted ( conn, addr ):
    DEBUG.LOGS.print( "Client joined", addr )
    conn.connect_passthrough( 8223 )

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
        socket_handler.process_connections()
        time.sleep(0.5)

        # reconnect any passthrough sockets that have become disconnected
        # this usually happens when the client is no longer welcome on the server
        # ie, when the game has ended, or game is starting, joining lobbies ect...
        pass