import os
import Common.signal_handler as signal_handler
import Common.DEBUG as DEBUG
import Common.database as db
import Sockets.ServerModuleSocket as ServerModuleSocket
import Sockets.SocketHandler as SocketHandler
import Common.constants as const
import Common.message as message
import time
import Common.Globals as Global
config = Global.GlobalConfig

def accept_client( connection, address ):
    request_client_identity( connection )

def request_client_identity( connection ):

    nickname = database.get_random_name()
    identity_request = message.Message( 'i' )
    identity_request.new_message( const.SERVER_NAME, "", nickname, "" )

    connection.send_message( identity_request )


def process_client_identity( message_obj ):

    from_conn = message_obj.from_connection
    nickname = message_obj["nickname"]
    reg_key = message_obj["reg_key"].strip()    # strip any white space
    client_id = -1

    # if the client returns a reg_key they may already exist.
    if len(reg_key) > 0:
        # find the users in the db by there reg key
        user = database.select_client(reg_key)

        if user is None:    # not found
            reg_key = ""
        else:
            client_id = user[0]
            if nickname != user[1]:
                database.update_client_nickname(reg_key, user[1])


    # if the reg key is empty assign a new one.
    if len(reg_key) == 0:
        # assign new reg key and nickname
        client_id, reg_key = database.add_new_client( nickname )

    status_message = message.Message( 'I' )
    status_message.new_message(const.SERVER_NAME, client_id, reg_key, True)

    message_obj.from_connection.send_message(status_message)

    # Disconnect the client once all message have been sent.
    from_conn.safe_close()
    DEBUG.LOGS.print("Done")

def process_connection( connection ):
    """Called for each connected connected client"""

    while connection.receive_message_pending():
        connection.receive_message().run_action()


if __name__ == "__main__":

    # import the config file.
    import Configs.docker_conf as conf

    running = True

    # set up
    terminate_signal = signal_handler.SignalHandler()
    Global.setup( conf )

    DEBUG.LOGS.init()
    DEBUG.LOGS.set_log_to_file(message=True, warning=True, error=True, fatal=True)

    database = db.Database()

    # bind message functions
    message.Message.bind_action("i", process_client_identity)

    # setup socket and bind to accept client socket
    socket_handler = SocketHandler.SocketHandler( config.get( "internal_host_auth" ), config.get( "internal_port" ),
                                                  15, ServerModuleSocket.ServerModuleSocket )

    socket_handler.accepted_client_bind( accept_client )

    # Welcome the server
    DEBUG.LOGS.print("Welcome",config.get("internal_host_auth"), ":", config.get("internal_port") )

    socket_handler.start()

    while running and not terminate_signal.triggered:
        # lets keep it clean :)
        socket_handler.process_connections( process_connection )
        # time.sleep(0.1)

    DEBUG.LOGS.print("Exiting...")

    socket_handler.close()
    DEBUG.LOGS.close()

    time.sleep(0.2)

    print(config.get("internal_host_auth"), ":", config.get("internal_port"), "- Offline")
    print("BeyBey!")
