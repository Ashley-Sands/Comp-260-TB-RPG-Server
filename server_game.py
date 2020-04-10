import Common.DEBUG as DEBUG
import Common.database as db
import Common.constants as const
import Common.message as message
import Common.actions
import Common.Protocols.status as status_protocol

import Sockets.ServerGameSocket as ServerGameSocket
import Sockets.SocketHandler as SocketHandler

import Components.Game.defaultGameMode as defaultGameMode

import time
import random
import Common.Protocols.status as statusProtocols

import Common.Globals as Global
config = Global.GlobalConfig

def process_connection( conn ):
    # process any messages from the client
    while conn.receive_message_pending():
        conn.receive_message().run_action()

def process_remove_connection( conn ):

    global close_game
    # check there is enough players still if not we'll have to end the game :(
    # When the player is disconnected the selector removes them from the database.

    player_count = database.get_lobby_player_count( lobby_id )

    if player_count < active_game_model.min_players:
        # disconect all others
        status = message.Message('!')
        # sent the from connection to the conn disconnecting so we can ignore it when we send the message
        status.from_connection = conn
        status.to_connections = socket_handler.get_connections()
        status.new_message( const.SERVER_NAME, status_protocol.SS_GAME_ENOUGH_PLAYERS,
                            False, "Not enough Players To continue." )
        status.send_message(True)

        # clear the game from the database.
        database.clear_game_host( game_host_id )

        # disconnect the remaining players from the server.
        connections = socket_handler.get_connections()
        for c in connections:
            if c == conn:
                continue
            DEBUG.LOGS.print(c.client_nickname, "::", c._client_db_id)
            c.safe_close()

        close_game = True


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
    msg.to_connections = socket_handler.get_connections() # send to all clients
    msg.send_message()


def process_client_status( message_obj ):

    # check that the client has reported that the scene has loaded successfully
    # and that they are now ready to receive the game setup info.
    if message_obj[ "status_type" ] == status_protocol.CS_SCENE_LOADED:
        if message_obj["ok"] :  # TODO: if the user is not ok, remove them from the game?
            if not message_obj.from_connection.ready:
                message_obj.from_connection.ready = True
                active_game_model.players_ready_count += 1

    # check all the players have arrived and readied
    # if so send the player info.
    expecting_player_count = database.get_lobby_player_count(lobby_id)

    DEBUG.LOGS.print( "Client Joined successfully! - ", message_obj.from_connection.client_nickname )

    if active_game_model.players_ready_count == expecting_player_count:
        # send out the player details to the clients
        available_player_ids = [x for x in range(expecting_player_count)] # list of player ids to assign each player at random without dups

        client_ids = []
        nicknames = []
        player_ids = []

        conn_sockets = socket_handler.connections

        for sock in conn_sockets:
            cid, nn, pid = socket_handler.get_connection( sock ).get_player_info()
            try:
                pid = random.choice( available_player_ids )
                available_player_ids.remove( pid )
            except Exception as e:
                DEBUG.LOGS.print( "No more random ids to choose for.", message_type=DEBUG.LOGS.MSG_TYPE_FATAL )

            client_ids.append( cid )
            nicknames.append( nn )
            player_ids.append( pid )

            conn_sockets[sock].player_id = pid

        game_info_msg = message.Message( "G" )
        game_info_msg.new_message( const.SERVER_NAME, client_ids, nicknames, player_ids )
        game_info_msg.to_connections = socket_handler.get_connections()
        game_info_msg.send_message()

if __name__ == "__main__":

    running = True
    game_active = False
    close_game = False
    active_game_model = None    # if the model is none then there is no active game currently

    game_host_id = -1
    lobby_id = -1

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
    message.Message.bind_action( '?', process_client_status )
    message.Message.bind_action( '&', Common.actions.processes_ping )
    message.Message.bind_action( 'i', process_client_identity )

    port = config.get( "internal_port" )

    # setup socket and bind to accept client socket
    socket_handler = SocketHandler.SocketHandler( config.get( "internal_host" ), port,
                                                  15, ServerGameSocket.ServerGameSocket )

    socket_handler.start()

    # Welcome the server
    DEBUG.LOGS.print("Welcome",config.get("internal_host"), ":", config.get("internal_port"), " - You game host id is: ", game_host_id )
    T = 0
    while running:
        # wait for a game to be added to the que
        while running and active_game_model is None:
            # assign the game id to the next lobby in the queue
            next_lobby_id = database.get_next_lobby_in_queue()
            if next_lobby_id is not None:
                database.update_lobby_game_host( next_lobby_id, game_host_id )
                DEBUG.LOGS.print("Lobby: ", next_lobby_id, "has been assigned", game_host_id, database.game_slot_assigned( next_lobby_id ))

                lobby_id = next_lobby_id
                active_game_model = defaultGameMode.DefaultGameMode( socket_handler, database )
                # bind game model functions to message.
                active_game_model.bind_all( message.Message )
                game_active = True

        # run the game.
        while running and game_active:

            socket_handler.process_connections( process_connection, process_remove_connection )
            if time.time() > T:
                DEBUG.LOGS.print("Running game - ", close_game)
                T = time.time() + 1

            if close_game and socket_handler.get_connection_count() > 0:
                DEBUG.LOGS.print( "Waiting for ", socket_handler.get_connection_count(), "To Disconnect" )
            elif close_game:
                game_active = False

        # unbind the game model functions from message
        # and reset the server status
        active_game_model.unbind_all( message.Message )
        active_game_model = None
        lobby_id = -1
        close_game = False

        DEBUG.LOGS.print("Next Lobby Please...")
