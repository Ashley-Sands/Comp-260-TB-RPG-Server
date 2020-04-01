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

    host = database.get_client_current_game_host( message_obj[ "reg_key" ] )

    # check that the client is on the correct host
    if host != config.get("internal_host"):
        DEBUG.LOGS.print( "Client has arrived at the wrong game host. expected:", config.get("internal_host"), "actual", host,
                          "Disconnecting...",
                          message_type=DEBUG.LOGS.MSG_TYPE_FATAL )
        from_conn.safe_close()

    # update the connection with the db data
    from_conn.lobby_id = client_lobby_id
    from_conn.client_nickname = client_nickname

    # notify other clients that they have joined the game server
    msg = message.Message('m')
    msg.new_message(client_nickname, [], "Has Joined the Server :D Yay! ")
    msg.to_connections = socket_handler.connections # send to all clients
    msg.send_message()


if __name__ == "__main__":

    running = True
    game_active = False
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
    socket_handler = SocketHandler.SocketHandler( config.get( "internal_host" ), port,
                                                  15, ServerGameSocket.ServerGameSocket )

    socket_handler.start()

    # Welcome the server
    DEBUG.LOGS.print("Welcome",config.get("internal_host"), ":", config.get("internal_port"), " - You game host id is: ", game_host_id )

    while running:
        # wait for a game to be added to the que
        while running and not game_active:

            pass

        # run the game.
        while running and game_active:
            # lets keep it clean :)
            socket_handler.process_connections( process_connection )
