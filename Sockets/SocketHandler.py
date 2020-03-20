import Common.DEBUG as DEBUG
import socket
import threading
import Common.constants as constants

class SocketHandler:

    def __init__( self, ip, port, max_conn, socket_client_class ):

        self.ip = ip
        self.port = port
        self.max_conn = max_conn
        self.accepting_connections = False

        self.socket_inst = None

        self.socket_client_class = socket_client_class
        self.connections = {}   # key socket, value is base socket client

        self.accept_connection_thread = None
        self.thread_lock = threading.Lock()

        self._accepted_client_callback = []

    def start( self ):
        """Starts allowing connections via the socket"""

        self.socket_inst = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_inst.bind( (self.ip, self.port) )
        self.socket_inst.listen( self.max_conn )

        self.accepting_connections = True

        self.accept_connection_thread = threading.Thread(target=self.accept_connection,
                                                         args=(self.socket_inst,) )
        self.accept_connection_thread.start()

    def accepted_client_bind( self, ac_callback ):
        """ binds to the accepted client function

        :param ac_callback:     function with param connection
        """

        self._accepted_client_callback.append( ac_callback )

    def invoke_accepted_callback( self, con_data ):

        for f in self._accepted_client_callback:
            f(con_data)

    def accept_connection( self, active_socket ):

        DEBUG.DEBUG.print("starting to accept connections")
        # we must allways accept the connection
        # even if we not accepting connections anymore,
        # other wise they build up and connect/disconnect
        # as soon as we start accepting connection again.
        while True:

            client_sock = active_socket.accept()[0]

            if not self.accepting_connections:
                continue

            self.thread_lock.acquire()

            self.connections[client_sock] = self.socket_client_class(client_sock)
            self.connections[client_sock].start()

            self.invoke_accepted_callback( self.connections[client_sock] )

            self.thread_lock.release()

        DEBUG.DEBUG.print("Not accepting connections anymore")

    def connection_exist( self, sock ):

        self.thread_lock.acquire()
        exist = sock in self.connections
        self.thread_lock.release()

        return exist

    def get_connection( self, sock ):
        """Get connections, if the connection does not exist returns None"""
        if sock in self.connections:

            self.thread_lock.acquire()
            conn = self.connections[sock]
            self.thread_lock.release()

            return conn
        else:
            return None

    def remove_connection( self, sock ):

        self.thread_lock.acquire()

        self.connections[sock].close()

        if sock in self.connections:
            del self.connections[sock]

        self.thread_lock.release()

    def clean_up( self ):
        """Cleans up any invalid connections"""

        self.thread_lock.acquire()

        # get all the keys from the connection so we can remove any invalid connections
        socks = list( self.connections )
        for s in socks:
            if self.connections[s].valid():
                self.connections[s].close() # make sure that all sockets are closed and thread has stopped.
                del self.connections[s]

        self.thread_lock.acquire()

