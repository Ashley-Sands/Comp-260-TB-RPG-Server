import Common.DEBUG as DEBUG
import Common.database as db
import Sockets.ServerLobbySocket as ServerLobbySocket
import Sockets.SocketHandler as SocketHandler
import Common.constants as const
import Common.message as message
import Common.actions
import time
import Common.Protocols.status as statusProtocols
import os
import Common.Globals as Global
config = Global.GlobalConfig


def process_connections( conn ):
    # process any messages from the client
    while conn.receive_message_pending():
        conn.receive_message().run_action()


def clean_lobby( connection ):

    lobby_id = connection.lobby_id

    # remove the client from the lobby
    if lobby_id in lobbies and connection.socket in lobbies[lobby_id]:
        del lobbies[lobby_id][connection.socket]


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
        host = database.get_lobby_host( client_lobby_id )
        if host == config.get("internal_host"):
            lobbies[ client_lobby_id ] = { from_conn.socket: from_conn }
        else:   # it appears the clients has arrived at the wrong location.
            DEBUG.LOGS.print( "Client has arrived at the wrong lobby host. expected:", config.get("internal_host"), "actual", host, "Disconnecting...",
                              message_type=DEBUG.LOGS.MSG_TYPE_FATAL )

            from_conn.safe_close()
            return

    # update the connection with the db data
    from_conn.lobby_id = client_lobby_id
    from_conn.client_nickname = client_nickname

    # send all the clients an updated list of connected clients
    cids, nnames = database.get_lobby_player_list( client_lobby_id )
    connected_clients = message.Message('C')
    connected_clients.new_message(const.SERVER_NAME, cids, nnames)
    connected_clients.to_connections = get_lobby_connections( client_lobby_id )
    connected_clients.send_message()

    # let every one know you have joined
    msg = message.Message('m')
    msg.new_message(client_nickname, [], "Has Joined the Server :D Yay! ")
    msg.to_connections = get_lobby_connections(client_lobby_id)
    msg.send_message()

    # send start status
    # TODO: ...

def process_message( message_obj ):

    # TODO: filter out connections that are not in to conn
    message_obj["from_client_name"] = message_obj.from_connection.client_nickname
    message_obj.to_connections = get_lobby_connections( message_obj.from_connection.lobby_id )
    message_obj.send_message()


def get_lobby_connections( lobby_id ):
    """gets the list of connections in lobby"""

    if lobby_id in lobbies:
        return list( lobbies[lobby_id].values() )

if __name__ == "__main__":

    running = True
    lobby_host_id = -1

    # the lobbies that exist on this host.
    lobbies = {}    # key = lobby id in db, value is dict of lobby connections key socket, value connection

    # set up
    Global.setup()

    DEBUG.LOGS.init()
    DEBUG.LOGS.set_log_to_file(message=True, warning=True, error=True, fatal=True)

    database = db.Database()

    # register the host into the database
    # wait for the sql server to come online
    while not database.database.test_connection():
        time.sleep(3)

    lobby_host_id = database.add_lobby_host( config.get( "internal_host" ) )

    # bind message functions
    message.Message.bind_action( 'P', Common.actions.processes_ping )
    message.Message.bind_action( 'i', process_client_identity )
    message.Message.bind_action( 'm', process_message )

    # setup socket and bind to accept client socket
    port = config.get( "internal_port" )
    socket_handler = SocketHandler.SocketHandler( config.get( "internal_host" ), port,
                                                  15, ServerLobbySocket.ServerLobbySocket )

    socket_handler.start()

    # Welcome the server
    DEBUG.LOGS.print("Welcome", config.get("internal_host"), ":", config.get("internal_port"), " - Your host id is: ", lobby_host_id )

    while running:
        # lets keep it clean :)
        socket_handler.process_connections( process_func=process_connections, extend_remove_connection_func=clean_lobby )
        time.sleep(0.5)

    database.remove_lobby_host( config.get( "internal_host" ) )
