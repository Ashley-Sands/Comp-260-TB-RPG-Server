from common.socket import SocketConnection, SocketClient
from common.database import Database
import message
import constants
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

    DEBUG.DEBUG.init()
    database = Database()   # TODO: Setup config.

    message.Message.initialize_actions(  )

    active_socket = SocketConnection("127.0.0.1", 8222, 20, SocketClient)
    active_socket.accepted_client_bind( accepted_client )
    active_socket.start()

    # Process each client
    while running:
        for sock in active_socket.connections:
            pass

