import Common.DEBUG as DEBUG
import socket
import threading
import Common.constants as constants

class SocketHandler:

    def __init__( self, ip, port, max_conn, base_socket ):

        self.ip = ip
        self.port = port
        self.max_conn = max_conn
        self.accepting_connections = True
        self.valid = True

        self.socket_inst = None

        self.socket_client_class = base_socket
        self.connections = {}   # key socket, value is base socket client

        self.thread_lock = threading.Lock()
        self.accept_connection_thread = None

        self._accepted_client_callback = []

    def start( self ):
        """Starts allowing connections via the socket"""

        self.socket_inst = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_inst.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.socket_inst.bind( (self.ip, self.port) )
        self.socket_inst.listen( self.max_conn )

        self.accepting_connections = True

        self.accept_connection_thread = threading.Thread( target=self.accept_connection,
                                                          args=(self.socket_inst,) )
        self.accept_connection_thread.start()

    def accepted_client_bind( self, ac_callback ):
        """ binds to the accepted client function

        :param ac_callback:     function with param connection and address
        """

        self._accepted_client_callback.append( ac_callback )

    def invoke_accepted_callback( self, connection, address_data ):

        for f in self._accepted_client_callback:
            f(connection, address_data)

    def accept_connection( self, active_socket ):

        DEBUG.LOGS.print("starting to accept connections")
        # we must always accept the connection
        # even if we not accepting connections anymore,
        # other wise they build up and connect/disconnect
        # as soon as we start accepting connection again.

        while self.valid:
            try:
                client_sock, addr = active_socket.accept()
            except Exception as e:
                DEBUG.LOGS.print("Could not accept connection ", e, message_type=DEBUG.LOGS.MSG_TYPE_ERROR)
                break

            DEBUG.LOGS.print( "Client Accepted" )

            if not self.accepting_connections:
                continue

            self.connections[client_sock] = self.socket_client_class(client_sock)
            self.connections[client_sock].start()

            if client_sock in self.connections:
                self.invoke_accepted_callback( self.connections[client_sock], addr )

        DEBUG.LOGS.print("Not accepting connections anymore")

    def new_connection( self, client_socket ):
        """Returns a new socket client class"""
        return self.socket_client_class( client_socket )

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

    def get_connection_count( self ):

        count = len( self.connections )

        return count

    def get_connections( self ):
        return list( self.connections.values() )

    def remove_connection( self, sock ):

        removed = False
        self.thread_lock.acquire()

        self.connections[sock].close()
        if sock in self.connections:
            del self.connections[sock]
            removed = True

        self.thread_lock.release()

        return removed

    def process_connections( self, process_func=None, extend_remove_connection_func=None ):
        """
            Cleans up any invalid connections, and call the process client function if supplied.
            This does not process any messages. consider using ModuleSocketHandler for processing message.
            In any case that is not an options process the clients messages in the process_func.
            WARNING: process_connections updates in fixed time steps. See constants.FIXED_TIME_STEP for update rate

        :param process_func:                    function with connection param to process each client
        :param extend_remove_connection_func:   extends the clean up functionality. requires connection param.
                                                this is call just before the connection is removed if supplied.
        :return:                                None
        """
        # get all the keys from the connection so we can remove any invalid connections
        socks = list( self.connections )

        for s in socks:
            # clear any invalid connections
            if not self.connections[ s ].valid():

                if extend_remove_connection_func is not None:
                    extend_remove_connection_func( self.connections[ s ] )

                DEBUG.LOGS.print( "Client ", self.connections[ s ]._client_db_id, "Not Valid, Removing..." )

                self.remove_connection(s)
                continue    # even if it fails to remove the connection skip any invalid

            # process the clients.
            if process_func is not None:
                process_func( self.connections[s] )

    def close( self ):
        """ closes all connections and terminates all threads """

        self.valid = False

        # close the main socket instance.
        try:
            self.socket_inst.shutdown( socket.SHUT_RDWR )
        except Exception as e:
            DEBUG.LOGS.print( "Bad socket: ", e, DEBUG.LOGS.MSG_TYPE_WARNING )

        try:
            self.socket_inst.close()
            DEBUG.LOGS.print( "Closed Main Socket " )
        except Exception as e:
            DEBUG.LOGS.print( "Failed to Close Main Socket ", e, DEBUG.LOGS.MSG_TYPE_WARNING )

        DEBUG.LOGS.print( "Closeing connections." )

        # close all of the connected clients connections
        for sock in self.connections:
            self.connections[sock].close()

        DEBUG.LOGS.print( "Connections closed Successfully." )

        # finally make sure that the accept connection has joined
        if self.accept_connection_thread.is_alive():
            self.accept_connection_thread.join()

        DEBUG.LOGS.print( "Socket handler closed successfully! :D" )
