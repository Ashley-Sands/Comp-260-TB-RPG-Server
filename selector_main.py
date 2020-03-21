import Common.DEBUG as DEBUG
import Common.database as db
import Sockets.ServerSelectSocket as ServerSelectSocket
import Sockets.SocketHandler as SocketHandler
import time

import Common.Globals as Global
config = Global.GlobalConfig

if __name__ == "__main__":
    import mysql_setup

    running = True

    Global.setup()

    DEBUG.LOGS.init()
    DEBUG.LOGS.set_log_to_file(message=True, warning=True, error=True)

    database = db.Database()

    # wait for db to connection
    while not database.database.test_connection():
        time.sleep(10) # try every 10 seconds

    mysql_setup.setup() # check that the sql is all set up correctly.

    socket_handler = SocketHandler.SocketHandler( config.get("host"), config.get("port"),
                                                  15, ServerSelectSocket.ServerSelectSocket)

    DEBUG.LOGS.print("Welcome",config.get("host"), ":", config.get("port") )

    socket_handler.start()

    while running:

        # clean up any zombie sockets
        socket_handler.clean_up()

        # reconnect any passthrough sockets that have become disconnected
        # this usually happens when the client is no longer welcome on the server
        # ie, when the game has ended, or game is starting, joining lobbies ect...
        pass