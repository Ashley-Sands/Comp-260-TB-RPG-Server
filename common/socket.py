import socket
import threading
import DEBUG
import time
import queue
import message
import constants

class SocketClient:
    """Base class for indervidule socket connections

    """
    MESSAGE_LEN_PACKET_SIZE = 2
    MESSAGE_TYPE_PACKET_SIZE = 1
    BYTE_ORDER = "big"

    def __init__( self, sock ):

        self.socket = sock
        self.client_key = ""    # this is the key that is stored in the DB!

        self.registration_timeout = time.time() + 30    # if the user fails to reg by this time they are kicked

        self.thread_lock = threading.Lock()
        self.inbound_thread = threading.Thread( target=self.receive_thread, args=(self.socket,))
        self.outbound_thread = threading.Thread( target=self.send_thread, args=(self.socket,))

        self.started = False
        self._valid = True

        # use the send_message and receive_message methods rather than accessing the que directly.
        self._outbound_queue = queue.Queue()        # send queue
        self._inbound_queue = queue.Queue()         # receive queue

    def start( self ):

        if self.started:
            return

        # start the inbound queue and outbound if there are message to send.
        self.inbound_thread.start()

        if not self._outbound_queue.empty():
            self.outbound_thread.start()

        self.started = True

    def valid( self, is_valid=None ):
        """thread safe method tp get and set _vaild
        if is_valid is None, it is not set
        """

        self.thread_lock.acquire()

        if is_valid is not None:
            self._valid = is_valid

        is_valid = self._valid

        self.thread_lock.release()

        return is_valid

    def from_name( self ):
        return constants.SERVER_NAME

    def send_message( self, message_obj ):

        if self.outbound_thread is None:
            self.outbound_thread = threading.Thread( target=self.send_thread, args=(self.socket,) )

        self._outbound_queue.put( message_obj )

        if not self.outbound_thread.is_alive():
            self.outbound_thread.start()

    def send_thread( self, sock ):

        DEBUG.DEBUG.print("starting send thread")

        while self.valid() and not self._outbound_queue.empty():
            # send all the messages
            message_obj = self._outbound_queue.get()

            msg_str = message_obj.get_message()
            msg_len = len( msg_str ).to_bytes(self.MESSAGE_LEN_PACKET_SIZE, self.BYTE_ORDER)
            msg_type = ord( message_obj.identity ).to_bytes(self.MESSAGE_TYPE_PACKET_SIZE, self.BYTE_ORDER)

            # check that the message is within the max message size
            if len( msg_str ) > pow( 255, self.MESSAGE_LEN_PACKET_SIZE ):
                DEBUG.DEBUG.print( "Message has exceeded the max message length." )
                return False

            try:
                print(msg_str, chr(ord( message_obj.identity )))
                self.socket.send( msg_len )
                self.socket.send( msg_type )
                self.socket.send( msg_str.encode() )
            except Exception as e:
                DEBUG.DEBUG.print( "Could not send data", e, message_type=DEBUG.DEBUG.MESSAGE_TYPE_ERROR )
                self.valid(False)

        self.outbound_thread = None

    def receive_message_pending( self ):
        return not self._inbound_queue.empty()

    def receive_message( self ):

        if not self._inbound_queue.empty():
            return self._inbound_queue.get()
        else:
            return None

    def receive_thread( self, sock ):
        """Receives message and puts it in the receive thread"""

        DEBUG.DEBUG.print("starting receive thread")
        msg_length = 0
        msg_type = ''

        while self.valid():

            try:
                # receive the first few bytes for message length and type
                msg_len_data = self.socket.recv( self.MESSAGE_LEN_PACKET_SIZE )

                # check that there is data. if we lose connection we will receive 0 bytes
                if len(msg_len_data) == 0:
                    self.valid( False )
                    break

                msg_type_data = self.socket.recv( self.MESSAGE_TYPE_PACKET_SIZE )

                msg_length = int.from_bytes( msg_len_data, self.BYTE_ORDER )
                msg_type = chr( int.from_bytes( msg_type_data, self.BYTE_ORDER ) )

            except Exception as e:
                DEBUG.DEBUG.print( "Could not receive data", DEBUG.DEBUG.MESSAGE_TYPE_ERROR )
                self.valid(False)
                break

            DEBUG.DEBUG.print("Received message from ", self.client_key, "Len:",
                              msg_length, "Type:", msg_type)

            # receive the json message of msg_type with length msg_length
            try:
                json_str = self.socket.recv( msg_length ).decode("utf-8")
            except Exception as e:
                DEBUG.DEBUG.print( "Could not receive data", e, message_type=DEBUG.DEBUG.MESSAGE_TYPE_ERROR )
                self.valid(False)
                break

            DEBUG.DEBUG.print( "message ", json_str)

            message_obj = message.Message(self.socket, msg_type)
            message_obj.set_message(self.from_name(), json_str)

            self._inbound_queue.put( message_obj )


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

        for s in self.connections:

            if self.connections[s].client_key == "":    # skip un registered clients
                continue

            if self.connections[s].client_key in message.to_clients:
                pass

    def socket_exist( self, sock ):
        return sock in self.connections

    def get_client_keys( self, except_sockets=[] ):

        return [ con.client_key for con in self.connections if con not in except_sockets ]

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
