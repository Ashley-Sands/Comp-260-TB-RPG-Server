from common.socket import SocketConnection, SocketClient
from common.database import Database
import message
import constants
import time
import DEBUG

# The entry server is responsable for registering the player into the network
# and send each client a list of available games every now and then

def accepted_client( connection ):
    # request the player identity. (this needs to be done in entry)
    identity = message.Message( constants.SERVER_NAME, 'i' )
    identity.message = identity.new_message( constants.SERVER_NAME, "", "" )

    connection.send_message(identity)

def send_lobby_list( connection ):
    pass

if __name__ == "__main__":

    running = True
    update_lobby_list_intervals = 15
    next_lobby_update = 0

    DEBUG.DEBUG.init()
    database = Database()   # TODO: Setup config.

    active_socket = SocketConnection("127.0.0.1", 8222, 20, SocketClient)
    active_socket.accepted_client_bind( accepted_client )

    message.Message.initialize_actions( database, active_socket.send_message,
                                        active_socket.get_client_keys, active_socket.get_connection )

    active_socket.start()

    # Process each client
    while running:
        # check that all clients are valid
        # and if its time update there lobby list
        for sock in active_socket.connections:
            if not active_socket.connections[sock].valid():
                # remove the client
                continue

            try:
                while active_socket.connections[sock].receive_message_pending():
                    msg = active_socket.connections[sock].receive_message()
                    msg.run_action()
            except Exception as e:
                DEBUG.DEBUG.print("Can not process message", e, message_type=DEBUG.DEBUG.MESSAGE_TYPE_ERROR)

            # TODO: move to thread??
            if time.time() > next_lobby_update and active_socket.connections[sock].registered:
                # send lobby update to all clients
                message.Message(constants.SERVER_NAME, '')

        if time.time() > next_lobby_update:
            next_lobby_update = time.time() + update_lobby_list_intervals
