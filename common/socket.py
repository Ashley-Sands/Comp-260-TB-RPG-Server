import socket
import threading
import DEBUG


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

    def invoke_accepted_callback( self, con ):

        for f in self._accepted_client_callback:
            f(con)

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
            self.connections[client_sock].start()

            self.invoke_accepted_callback( self.connections[client_sock] )

            self.thread_lock.release()

        DEBUG.DEBUG.print("Not accepting connections anymore")



    def send_message( self, message ):

        self.thread_lock.acquire()

        for s in self.connections:

            if self.connections[s].client_key == "":    # skip un registered clients
                continue

            if self.connections[s].client_key in message.to_clients:
                pass

        self.thread_lock.release()

    def socket_exist( self, sock ):

        self.thread_lock.acquire()
        exist = sock in self.connections
        self.thread_lock.release()

        return exist

    def get_client_keys( self, except_sockets=[] ):

        self.thread_lock.acquire()

        keys = [ con.client_key for con in self.connections if con not in except_sockets ]

        self.thread_lock.release()
        return keys

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
