import Common.DEBUG as DEBUG
import Common.database as db
import Sockets.ServerLobbySocket as ServerLobbySocket   #####
import Sockets.SocketHandler as SocketHandler
import Common.constants as const
import Common.message as message
import time
import Common.Protocols.status as statusProtocols
import os
import Common.Globals as Global
config = Global.GlobalConfig


def process_client_identity( message_obj ):

    DEBUG.LOGS.print( "Recivedd id", message_obj[ "client_id" ], message_obj[ "reg_key" ] )

    from_conn = message_obj.from_connection
    # add the clients data to the connection
    from_conn.set_client_key( message_obj[ "client_id" ], message_obj[ "reg_key" ] )
    from_conn.client_nickname = message_obj[ "nickname" ]

    # TODO: Find the users lobby via the db.

if __name__ == "__main__":

    running = True

    # set up
    Global.setup()

    DEBUG.LOGS.init()
    DEBUG.LOGS.set_log_to_file(message=True, warning=True, error=True, fatal=True)

    database = db.Database()

    # register the host into the database
    # wait for the sql server to come online
    while not database.database.test_connection():
        time.sleep(10)

    database.add_lobby_host( config.get( "internal_host" ) )
    print( database.database.select_from_table( "lobby_host", ["*"] ) )
    # bind message functions
    message.Message.bind_action( 'i', process_client_identity )

    # setup socket and bind to accept client socket
    port = config.get( "internal_port" )
    socket_handler = SocketHandler.SocketHandler( config.get( "internal_host" ), port,
                                                  15, ServerLobbySocket.ServerLobbySocket )

    socket_handler.start()

    # Welcome the server
    DEBUG.LOGS.print("Welcome",config.get("internal_host"), ":", config.get("internal_port") )

    while running:
        # lets keep it clean :)
        socket_handler.process_connections( )
        time.sleep(0.5)

    database.remove_lobby_host( config.get( "internal_host" ) )
