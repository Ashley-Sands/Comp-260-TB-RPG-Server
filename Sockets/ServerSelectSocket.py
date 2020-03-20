import Common.DEBUG as DEBUG
import socket
import Sockets.BaseSocket as BaseSocket
import threading
import Common.constants as constants


class ServerSelectSocket( BaseSocket.BaseSocketClient ):
    """ServerSelectSocket re-directs the clients to the correct location within the network"""

    def __init__(self, client_socket):

        super().__init__( client_socket )

        self._passthrough_mode = False
        self.passthrough_socket = None

    def connect_passthrough( self, ip, port  ):
        """
            Connect the passthrough
        :param ip:      the ip or host name (string)
        :param port:    the port            (int)
        :return:        None
        """

        if not self.passthrough_mode():  # can only create new socket when not in passthrough
            self.passthrough_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.passthrough_socket = socket.socket.connect( (ip, port) )
                self.passthrough_mode(True)
            except Exception as e:
                DEBUG.LOGS.print("Could not connect passthrough (", ip, port,")", message_type=DEBUG.LOGS.MSG_TYPE_ERROR)
                return

            # start the outbound thread now we have connected to the server.
            self.outbound_thread = threading.Thread( target=self.passthrough_send_thread,
                                                     args=(self.socket, self.passthrough_socket) )
            self.outbound_thread.start()

    def start( self ):

        # initialize the inbound from the client
        # the outbound can be started when passthrough connects to the server

        self.inbound_thread = threading.Thread( target=self.passthrough_receive_thread,
                                                args=(self.socket, self.passthrough_socket) )

        self.inbound_thread.start()

        super().start()

    def passthrough_mode( self, active=None ):
        """
        Thread safe method to get and set _passthrough_mode
        If is_valid is None, it is not set
        """

        self.thread_lock.acquire()

        if active is not None:
            self._passthrough_mode = active

        active = self._passthrough_mode

        self.thread_lock.release()

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

            return message_length_data + message_data

        except Exception as e:
            DEBUG.LOGS.print( socket_name, "socket has died (", e, ")",
                              message_type=DEBUG.LOGS.MSG_TYPE_WARNING )
            return None

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

    def passthrough_receive_thread( self, client_socket, passthrough_socket ):
        """
            Inbound to the server /
            Outbound from the client
            Receives data from the client sending the data back out through the passthrough socket.
        """

        while self.valid():

            # receive all the data from the client sending it directly back out the other server
            data = self.receive_passthrough_data( client_socket, "client")

            if data is None:
                self.valid( False )
                break

            if not self.passthrough_mode():
                continue    # discard the data as theres no where to send it.

            # send the data onto the server
            if not self.send_data( passthrough_socket, data, "passthrough") :
                self.passthrough_mode( False )

    def passthrough_send_thread( self, client_socket, passthrough_socket ):
        """
            Outbound from the server /
            Inbound to the client
            Receives data from the passthrough sending the data back out to the client socket
        """

        while self.valid() and self.passthrough_mode():

            # receive all the data from the server sending it directly back out to the client
            data = self.receive_passthrough_data( passthrough_socket, "client" )

            if data is None:
                self.passthrough_mode( False )
                break

            # send the data onto the client
            if not self.send_data( client_socket, data, "passthrough" ):
                self.valid( False )


    def close_socket( self ):

        super().close_socket()
        self.passthrough_socket.close()
