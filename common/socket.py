import socket
import threading
import DEBUG
import time

class SocketClient:
    """Base class for indervidule socket connections

    """

    def __init__( self, sock ):

        self.socket = sock
        self.client_key = ""    # this is the key that is stored in the DB!

        self.registration_timeout = time.time() + 30    # if the user fails to reg by this time they are kicked

        self._valid = True

class SocketConnection:

    def __init__( self, ip, port, max_conn, socket_client_class ):

        self.ip = ip
        self.port = port
        self.max_conn = max_conn
        self.accepting_connections = False

        self.socket_inst = None

        self.socket_client_class = socket_client_class
        self.connections = {}   # key socket, value is socket client

        self.accept_connection_thread = None
        self.thread_lock = threading.Lock()


    def start( self ):
        """Starts allowing connections via the socket"""

        self.socket_inst = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_inst.bind( (self.ip, self.port) )
        self.socket_inst.listen( self.max_conn )

        self.accepting_connections = True

        self.accept_connection_thread = threading.Thread(target=self.accept_connection,
                                                         args=(self.socket_inst,) )
        self.accept_connection_thread.start()


    def accept_connection( self, active_socket ):

        DEBUG.DEBUG.print("starting to accept connections")
        # we must allways accept the connection
        # even if we not accepting connections anymore,
        # other wise they build up and connect/disconnect
        # as soon as we start accepting connection again.
        while True:

            client_sock = self.socket_inst.accept()[0]

            self.thread_lock.acquire()

            if not self.accepting_connections:
                continue

            self.connections[client_sock] = self.socket_client_class(client_sock)

            # request that the player identity.
            # TODO: ...

            self.thread_lock.release()

    def send_message( self, sock, message ):
        # TODO: ...
        pass

    def send_message_to_client_key( self, client_key, message ):

        sock = self.get_socket_from_client_key(client_key)

        if sock is not None:
            self.send_message(sock, message)

    def socket_exist( self, sock ):
        return sock in self.connections

    def get_socket_from_client_key( self, client_key ):
        """Get the clients socket via the clients key.
        returns None if key not found.
        """
        for s in self.connections:
            if self.connections[s].client_key == "":    # unregistered  client
                continue
            if self.connections[s].client_key == client_key:
                return s

        return None

    def get_connection( self, sock ):
        """Get connections, if the connection does not exist returns None"""
        if sock in self.connections:
            return self.connections[sock]
        else:
            return None
