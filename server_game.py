import Common.DEBUG as DEBUG
import Common.database as db
import Sockets.ServerGameSocket as ServerGameSocket
import Sockets.SocketHandler as SocketHandler
import Common.constants as const
import Common.message as message
import Common.actions
import time
import Common.Protocols.status as statusProtocols

import Common.Globals as Global
config = Global.GlobalConfig

def process_connection( conn ):
    pass

def process_client_identity( message_obj ):

    DEBUG.LOGS.print( "Recivedd id", message_obj[ "client_id" ], message_obj[ "reg_key" ] )

    from_conn = message_obj.from_connection

    # TODO: have a look at makeing this bit common its the same in lobby
    # add the clients data to the connection
    from_conn.set_client_key( message_obj[ "client_id" ], message_obj[ "reg_key" ] )

    # find the user in the database and make sure they have arrived at the correct location
    client_info = database.select_client( message_obj[ "reg_key" ] )
    client_nickname = client_info[1]
    client_lobby_id = client_info[2]

    # check that the client is on the correct host

    # update the connection with the db data
    from_conn.lobby_id = client_lobby_id
    from_conn.client_nickname = client_nickname

    # notify other clients that they have joined the game server


if __name__ == "__main__":

    running = True
    game_host_id = -1

    # set up
    Global.setup()

    DEBUG.LOGS.init()
    DEBUG.LOGS.set_log_to_file(message=True, warning=True, error=True, fatal=True)

    database = db.Database()

    # register the host into the database
    # wait for the sql server to come online
    while not database.database.test_connection():
        time.sleep(5)

    game_host_id = database.add_game_host( config.get( "internal_host" ) )

    # bind message functions
    message.Message.bind_action( '&', Common.actions.processes_ping )
    message.Message.bind_action( 'i', process_client_identity )

    port = config.get( "internal_port" )

    # setup socket and bind to accept client socket
    socket_handler = SocketHandler.SocketHandler( config.get( "internal_host_lobbies" ), port,
                                                  15, ServerGameSocket.ServerGameSocket )

    socket_handler.start()

    # Welcome the server
    DEBUG.LOGS.print("Welcome",config.get("internal_host_lobbies"), ":", config.get("internal_port") )

    while running:
        # lets keep it clean :)
        socket_handler.process_connections( process_connection )
