from common.socket import SocketConnection, SocketClient
from common.database import Database
import DEBUG


if __name__ == "__main__":

    running = True

    DEBUG.DEBUG.init()
    database = Database()   # TODO: Setup config.
    database.add_new_client("Helloo World")

    active_socket = SocketConnection("127.0.0.1", 8222, 4, SocketClient)
    active_socket.start()

    # Process each client
    while running:
        for sock in active_socket.connections:
            pass

