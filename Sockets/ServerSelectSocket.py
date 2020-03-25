import Common.DEBUG as DEBUG
import socket
import Sockets.BaseSocket as BaseSocket
import threading
import Common.database as Database
import Common.constants as constants
import queue
import Common.message as message
import Common.Globals
config = Common.Globals.GlobalConfig


class ServerSelectSocket( BaseSocket.BaseSocketClient ):
    """ServerSelectSocket re-directs the clients to the correct location within the network"""

    CONN_TYPE_DEFAULT   = 0     # default passthrough mode
    CONN_TYPE_AUTH      = 1     # auth mode intersects messages from the passthrough connection
    CONN_TYPE_OUTBOUND  = 2     # sends messages to the client only (get send when internal server disconnects)

    def __init__(self, client_socket):

        super().__init__( client_socket )

        self._conn_mode = ServerSelectSocket.CONN_TYPE_OUTBOUND

        # waits until all outgoing messages have been sent to connect the passthrough
        self.connect_passthrough_thread = None
        self.non_passthrough_outbound_thread = None
        self._outbound_queue = queue.Queue()

        self._passthrough_mode = False
        self.passthrough_socket = None

    def conn_mode( self, mode=None ):
        """thread safe mode to gets and set conn mode"""

        self.thread_lock.acquire()

        if mode is None:
            mode = self._conn_mode
        else:
            self._conn_mode = mode

        self.thread_lock.release()

        return mode

    def connect_passthrough( self, conn_mode, host, port ):
        """
            Connect the passthrough
        :param conn_mode:   the mode to change to. (ignores outbound mode.)
        :param host:        the ip or host name (string)
        :param port:        the port            (int)
        :return:            None
        """

        # can not que type outbound.
        # the outbound mode is set when the internal server disconnects
        if conn_mode == self.CONN_TYPE_OUTBOUND:
            return

        if self.connect_passthrough_thread is None:
            self.connect_passthrough_thread = threading.Thread( target=self.que_connect_passthrough_thread,
                                                                args=( conn_mode, host, port) )
            self.connect_passthrough_thread.start()

    def que_connect_passthrough_thread( self, conn_mode, host, port ):

        DEBUG.LOGS.print("Connecting passthrough to server @ ", (host, port) )

        # wait until all messages have been sent while in outbound mode
        while self.CONN_TYPE_OUTBOUND and not self._outbound_queue.empty():
            pass    # should sleep.

        if not self.passthrough_mode():  # can only create new socket when not in passthrough
            self.passthrough_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.passthrough_socket.connect( (host, port) )
                # the auth server will request the data once it ready
                if conn_mode != self.CONN_TYPE_AUTH:
                    self.send_client_data_to_server( self.passthrough_socket )

                self.passthrough_mode(True)
            except Exception as e:
                DEBUG.LOGS.print("Could not connect passthrough", (host, port), e, message_type=DEBUG.LOGS.MSG_TYPE_ERROR)
                self.passthrough_mode( False )
                return

            # start the outbound thread now we have connected to the server.
            self.outbound_thread = threading.Thread( target=self.passthrough_send_thread,
                                                     args=(self.socket, ) )
            self.outbound_thread.start()
            self.conn_mode( conn_mode )

        self.connect_passthrough_thread = None

    def send_client_data_to_server( self, pass_sock ):
        """Send the clients data to the server we have just connected to"""

        identity_msg = message.Message("i")
        identity_msg.new_message( constants.SERVER_NAME, self.get_client_key()[0], "", self.get_client_key()[1] )

        msg = identity_msg.get_json()
        len_data = len(msg).to_bytes(self.MESSAGE_LEN_PACKET_SIZE, self.BYTE_ORDER)
        chr_data = ord('i').to_bytes(self.MESSAGE_TYPE_PACKET_SIZE, self.BYTE_ORDER)

        return self.send_data( pass_sock, len_data + chr_data + msg.encode(), "id sender" )

    def start( self ):

        # initialize the inbound from the client
        # the outbound can be started when passthrough connects to the server

        self.inbound_thread = threading.Thread( target=self.passthrough_receive_thread,
                                                args=(self.socket, ) )

        self.inbound_thread.start()

        super().start()

    def passthrough_mode( self, active=None ):
        """
        Thread safe method to get and set _passthrough_mode
        If is_valid is None, it is not set
        """


        if active is not None:
            self.thread_lock.acquire()
            self._passthrough_mode = active
            self.thread_lock.release()

        active = self._passthrough_mode

        if not active:
            self.conn_mode(self.CONN_TYPE_OUTBOUND)


        return active

    def receive_passthrough_data( self, sock, socket_name ):
        """
            sends data to sock
        :param sock:            the socket to send to
        :param socket_name:     the name of the socket (used for error message)
        :return:                data in bytes if successful other None if failed
        """
        try:

            # receive the first 2 bytes so we know much data is in coming,
            # not forgetting about the identity char after the len buffer
            message_length_data = sock.recv( self.MESSAGE_LEN_PACKET_SIZE )

            # check that there is data. if we lose connection we will receive 0 bytes
            if len( message_length_data ) == 0:
                return None

            message_length = int.from_bytes( message_length_data, self.BYTE_ORDER )
            message_length += self.MESSAGE_TYPE_PACKET_SIZE

            # get identity char and message body
            message_data = sock.recv( message_length )

            if self.conn_mode() == self.CONN_TYPE_AUTH:
                self.intersect_data( message_data[0], message_data[1:] )

            return message_length_data + message_data

        except Exception as e:
            DEBUG.LOGS.print( socket_name, "socket has died (", e, ")",
                              message_type=DEBUG.LOGS.MSG_TYPE_WARNING )
            return None

    def intersect_data( self, id_byte, json_bytes ):
        """

        :param id_byte:     the identity char byte
        :param json_bytes:  json bytes
        :return:
        """

        identity = chr( id_byte )
        if identity == 'I':
            msg = message.Message( identity )
            msg.set_from_json( constants.SERVER_NAME, json_bytes.decode() )
            self.set_client_key( msg["client_id"], msg["reg_key"] )
            DEBUG.LOGS.print("Client Idenity Set. id", msg["client_id"], "reg key", msg["reg_key"])

    def send_data ( self, sock, data, socket_name ):
        """
            sends data to sock
        :param sock:            the socket to send to
        :param data:            the data in bytes to send
        :param socket_name:     the name of the socket (used for error message)
        :return:                True if successful otherwise False
        """
        try:
            sock.send( data )

            return True

        except Exception as e:
            DEBUG.LOGS.print( socket_name, "socket has died (", e, ")",
                              message_type=DEBUG.LOGS.MSG_TYPE_WARNING)

            return False

    def passthrough_receive_thread( self, client_socket ):
        """
            Inbound to the server /
            Outbound from the client
            Receives data from the client sending the data back out through the passthrough socket.
        """

        # TODO: Issue: we can NOT send the pass through socket into thread function
        # as it is possible for the thread to begin before the connection is made.
        # i might need to make a dupe of the socket in the thread.
        # we'll see how it goes.

        while self.valid():

            # receive all the data from the client sending it directly back out the other server
            data = self.receive_passthrough_data( client_socket, "client recv")

            if data is None:
                self.valid( False )
                break

            if not self.passthrough_mode():
                continue    # discard the data as theres no where to send it.

            # send the data onto the server
            if not self.send_data( self.passthrough_socket, data, "passthrough recv") :
                self.passthrough_mode( False )

    def passthrough_send_thread( self, client_socket ):
        """
            Outbound from the server /
            Inbound to the client
            Receives data from the passthrough sending the data back out to the client socket
        """
        # TODO: Issue: we can NOT send the pass through socket into thread function
        # as it is possible for the thread to begin before the connection is made.
        # i might need to make a dupe of the socket in the thread.
        # we'll see how it goes.

        while self.valid() and self.passthrough_mode():

            # receive all the data from the server sending it directly back out to the client
            data = self.receive_passthrough_data( self.passthrough_socket, "client snd" )

            if data is None:
                self.passthrough_mode( False )
                break

            # send the data onto the client
            if not self.send_data( client_socket, data, "passthrough snd" ):
                self.valid( False )

    def send_message( self, message_obj ):
        """ques messages to be send if in outbound mode."""

        if self.conn_mode() == self.CONN_TYPE_OUTBOUND:

            self._outbound_queue.put( message_obj )
            if self.non_passthrough_outbound_thread is None:
                self.non_passthrough_outbound_thread = threading.Thread( target=self.send_thread, args=(self.socket, ) )
                self.non_passthrough_outbound_thread.start()

    def send_thread( self, client_socket ):
        """Send thread when not in pass through mode"""

        # send for as long as we are vaild, in outbound mode and have messages to senf.
        while self.valid() and self.conn_mode() == self.CONN_TYPE_OUTBOUND and not self._outbound_queue.empty():
            message_obj = self._outbound_queue.get()
            msg_str = message_obj.get_json()

            # convert the message len and identity char to bytes
            msg_len = len( msg_str ).to_bytes( self.MESSAGE_LEN_PACKET_SIZE, self.BYTE_ORDER )
            msg_type = ord( message_obj.identity ).to_bytes( self.MESSAGE_TYPE_PACKET_SIZE, self.BYTE_ORDER )

            # check that the message is within the max message size
            if len( msg_str ) > pow( 255, self.MESSAGE_LEN_PACKET_SIZE ):
                DEBUG.LOGS.print( "Message has exceeded the max message length.",
                                  message_type=DEBUG.LOGS.MSG_TYPE_ERROR )
                return

            if not self.send_data( client_socket, (msg_len + msg_type + msg_str.encode()) , "socket outbound" ):
                self.valid( False )

        self.non_passthrough_outbound_thread = None


    def close_socket( self ):
        super().close_socket()
        try:
            self.passthrough_socket.shutdown( socket.SHUT_RDWR )
        except:
            pass

        try:
            self.passthrough_socket.close()
        except Exception as e:
            DEBUG.LOGS.print("can not close passthrough socket", e, message_type=DEBUG.LOGS.MSG_TYPE_ERROR)

    def join_threads( self ):

        super().join_threads()
        if self.non_passthrough_outbound_thread is not None and self.non_passthrough_outbound_thread.is_alive():
            self.non_passthrough_outbound_thread.join()

    def close( self ):

        super().close()
        self.passthrough_mode(False)
