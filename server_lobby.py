import Common.DEBUG as DEBUG
import Common.database as db
import Sockets.ServerLobbySocket as ServerLobbySocket
import Sockets.ModuleSocketHandler as SocketHandler
import Common.signal_handler as signal_handler
import Common.constants as const
import Common.message as message
import Common.actions
import time
import Common.Protocols.status as statusProtocols
import os
import Common.Globals as Global
config = Global.GlobalConfig

MAX_GAME_START_TIME = 30
GAME_START_TIME = 15        # seconds until the game can start once there is enough players
NEW_PLAYER_DELAY = 5


def process_connections( conn ):
    # process any messages from the client
    while conn.receive_message_pending():
        conn.receive_message().run_action()


def clean_lobby( connection ):

    lobby_id = connection.lobby_id
    client_nickname = connection.client_nickname
    # remove the client from the lobby
    if lobby_id in lobbies and connection.socket in lobbies[lobby_id]:
        del lobbies[lobby_id][connection.socket]

        # notify all the others that a client has left.
        msg = message.Message( 'm' )
        msg.new_message( client_nickname, [ ], "Has Left the Server :( " )
        msg.to_connections = get_lobby_connections( lobby_id )
        msg.send_message()

        send_client_list( lobby_id )

        send_lobby_info( lobby_id )


def process_client_identity( message_obj ):

    DEBUG.LOGS.print( "Recivedd id", message_obj[ "client_id" ], message_obj[ "reg_key" ] )

    from_conn = message_obj.from_connection

    # add the clients data to the connection
    from_conn.set_client_key( message_obj[ "client_id" ], message_obj[ "reg_key" ] )

    # find the user in the database and make sure they have arrived at the correct location
    client_info = database.select_client( message_obj[ "reg_key" ] )
    client_nickname = client_info[1]
    client_lobby_id = client_info[2]

    # find if the lobby exist on the server
    # if not double check that the client has arrive at the correct location
    # and create a new lobby.
    if client_lobby_id in lobbies:
        lobbies[ client_lobby_id ][ from_conn.socket ] = from_conn
    else:
        host = database.get_lobby_host_from_lobby_id( client_lobby_id )
        if host == config.get("internal_host"):
            lobbies[ client_lobby_id ] = { from_conn.socket: from_conn }
            lobbies_start_times [ client_lobby_id ] = -1
        else:   # it appears the clients has arrived at the wrong location.
            DEBUG.LOGS.print( "Client has arrived at the wrong lobby host. expected:", host, "actual", config.get("internal_host"), "Disconnecting...",
                              message_type=DEBUG.LOGS.MSG_TYPE_FATAL )

            from_conn.safe_close()
            return

    # update the connection with the db data
    from_conn.lobby_id = client_lobby_id
    from_conn.client_nickname = client_nickname

    # send all the clients an updated list of connected clients
    send_client_list( client_lobby_id )

    # let everyone know you have joined
    msg = message.Message('m')
    msg.new_message(client_nickname, [], "Has Joined the Server :D Yay! ")
    msg.to_connections = get_lobby_connections(client_lobby_id)
    msg.send_message()

    # send start status
    send_lobby_info( client_lobby_id )


def process_message( message_obj ):

    # TODO: filter out connections that are not in to conn
    message_obj["from_client_name"] = message_obj.from_connection.client_nickname
    message_obj.to_connections = get_lobby_connections( message_obj.from_connection.lobby_id )
    message_obj.send_message()


def send_lobby_info(lobby_id):

    level_name, min_players, max_players = database.get_lobby_info( lobby_id )

    # set/unset the game start time as required
    if lobbies_start_times[ lobby_id ] < 0 and get_clients_in_lobby( lobby_id ) >= min_players:
        # queue the game now theres enough players
        lobbies_start_times[ lobby_id ] = time.time() + GAME_START_TIME
        queue_lobbie( lobby_id, False )

    elif lobbies_start_times[ lobby_id ] > 0 and get_clients_in_lobby( lobby_id ) < min_players:
        # dequeue the game, now we've lost some players
        lobbies_start_times[ lobby_id ] = -1
        queue_lobbie( lobby_id, True )

    elif lobbies_start_times[ lobby_id ] > 0:  # add a little more time if a new player connects.
        lobbies_start_times[ lobby_id ] += NEW_PLAYER_DELAY

    lobby_info = message.Message( 'O' )
    lobby_info.new_message( const.SERVER_NAME, level_name, min_players, max_players, lobbies_start_times[ lobby_id ] - time.time() )
    lobby_info.to_connections = get_lobby_connections( lobby_id )
    lobby_info.send_message()

def send_client_list( lobby_id ):

    cids, nnames = database.get_lobby_player_list( lobby_id )
    connected_clients = message.Message('C')
    connected_clients.new_message(const.SERVER_NAME, cids, nnames)
    connected_clients.to_connections = get_lobby_connections( lobby_id )
    connected_clients.send_message()


def client_status( message_obj ):

    if message_obj[ "status_type" ] == statusProtocols.CS_LEAVE_GAME:
        from_conn = message_obj.from_connection

        # clear the clients lobby in the database and disconnect client
        database.clear_client_lobby( from_conn.get_client_key()[1] )

        from_conn.safe_close()
        DEBUG.LOGS.print("Client Left Lobby")


def get_lobby_connections( lobby_id ):
    """gets the list of connections in lobby"""

    if lobby_id in lobbies:
        return list( lobbies[lobby_id].values() )


def get_clients_in_lobby( lobby_id ):

    if lobby_id in lobbies:
        return len( lobbies[lobby_id] )


def queue_lobbie( lobby_id, dequeue ):

    if dequeue:
        database.remove_lobby_from_game_queue(lobby_id)
    else:
        database.add_lobby_to_game_queue(lobby_id)


def assign_game_slot(): # this will be done from the game instance. while its free to do stuff :)
    # once a lobby is queued the next available game slot will be assigned even if the
    # lobby is not ready to launch.
    pass


def launch_game( lobby_id ):
    """Lunches the game if a game slot has been assigned
    return: true if the game was launched otherwise false
    """
    # so one the count down is complete, we are able to launch
    # as long as a game slot has been assigned.
    # if not we'll just have to stick around until one is freed up
    # and just hope that the players stick around.
    # in the real world i would just throw more resources at it

    if database.game_slot_assigned( lobby_id ):
        # unset the lobby host id and kick them out.
        # Its game time!! :P
        database.clear_lobby_host( lobby_id )
        print( "Cleared lobby id", lobby_id )
        for client in lobbies[ lobby_id ]:
            lobbies[ lobby_id ][client].safe_close()

        # remove the lobby from the server.
        del lobbies[ lobby_id ]
        del lobbies_start_times[ lobby_id ]

        DEBUG.LOGS.print( "Bey Bey, Lobby", lobby_id )
        return True
    else:
        database.debug()
        que_size = database.get_game_queue_size()
        DEBUG.LOGS.print("lh_id", lobby_host_id, "lid", lobby_id, "Waiting for game to be assigned...",
                         "queue size", que_size, message_type=DEBUG.LOGS.MSG_TYPE_WARNING )
        return False

if __name__ == "__main__":

    running = True
    lobby_host_id = -1

    # the lobbies that exist on this host.
    lobbies = {}    # key = lobby id in db, value is dict of lobby connections key socket, value connection
    lobbies_start_times = {} # key = lobby id value if > 0 start time else not enough players

    # set up
    terminate_signal = signal_handler.SignalHandler()
    Global.setup()

    DEBUG.LOGS.init()
    DEBUG.LOGS.set_log_to_file(message=True, warning=True, error=True, fatal=True)

    database = db.Database()

    # register the host into the database
    # wait for the sql server to come online
    while not database.database.test_connection():
        time.sleep(5)

    lobby_host_id = database.add_lobby_host( config.get( "internal_host" ) )

    # bind message functions
    message.Message.bind_action( '&', Common.actions.processes_ping )
    message.Message.bind_action( '?', client_status )
    message.Message.bind_action( 'i', process_client_identity )
    message.Message.bind_action( 'm', process_message )

    # setup socket and bind to accept client socket
    port = config.get( "internal_port" )
    socket_handler = SocketHandler.ModuleSocketHandler( config.get( "internal_host" ), port,
                                                  15, ServerLobbySocket.ServerLobbySocket )

    socket_handler.start()

    # Welcome the server
    DEBUG.LOGS.print("Welcome", config.get("internal_host"), ":", config.get("internal_port"), " - Your lobby host id is: ", lobby_host_id )

    while running and not terminate_signal.triggered:

        socket_handler.process_connections( process_func=process_connections,
                                            extend_remove_connection_func=clean_lobby )

        # process change to game.
        # TODO: pre-compute lobby key ids.
        # we really should not do this evey update.
        lobby_ids = list( lobbies_start_times.keys() )

        for lid in lobby_ids:
            if lobbies_start_times[ lid ] > 0 and time.time() > lobbies_start_times[lid ]:
                # start the lobby
                if not launch_game( lid ):
                    lobbies_start_times[ lid ] += 2  # don't check for another couple of seconds

    DEBUG.LOGS.print("Exiting...")

    # clean up any existing data in the database.
    database.remove_lobby_host( config.get( "internal_host" ) )
    database.clear_lobby_host_from_all_lobbies( lobby_host_id )

    # clear any assigned lobbies from all clients
    for lid in lobbies:
        database.clear_lobby_from_all_users(lid)

    socket_handler.close()
    DEBUG.LOGS.close()

    time.sleep(0.2)

    print(config.get("internal_host"), config.get("internal_host_lobbies"), ":", config.get("internal_port"), " - Offline")
    print("BeyBey!")
