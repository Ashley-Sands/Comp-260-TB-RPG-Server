import Common.DEBUG as DEBUG
import Sockets.BaseSocket as BaseSocket
import threading
import Common.constants as constants


class ServerSelectSocket( BaseSocket.BaseSocketClient ):
    """ServerSelectSocket re-directs the clients to the correct location within the network"""

    def __init__(self, client_socket, passthrough_socket):

        super().__init__( client_socket )

        self.passthrough_mode = False
        self.passthrough_socket = passthrough_socket

    def start( self ):

        # initialize the inbound and outbound threads
        # for passthrough both must be running.

        self.inbound_thread = threading.Thread( target=self.passthrough_receive_thread,
                                                args=(self.socket, self.passthrough_socket) )

        self.outbound_thread = threading.Thread( target=self.passthrough_send_thread,
                                                 args=(self.socket, self.passthrough_socket) )

        self.inbound_thread.start()
        self.outbound_thread.start()

        super().start()

    def passthrough_receive_thread( self, client_socket, passthrough_socket ):
        """
            Inbound to the server /
            Outbound from the client
            Receives data from the client sending the data back out through the passthrough socket.
        """
        # TODO: verify data. atm ifs direct passthrough
        while self.valid():
            pass

        pass

    def passthrough_send_thread( self, client_socket, passthrough_socket ):
        """
            Outbound from the server /
            Inbound to the client
            Receives data from the passthrough sending the data back out to the client socket
        """
        # TODO: intersect special messages from the server
        # TODO: verify data. atm ifs direct passthrough
        while self.valid():
            pass

        pass

    def send_thread( self, client_socket ):
        """
            Outbound from the select server /
            Inbound to the client
            When the select server is changing services/server it is able to send messages directly
            to the client. While in passthrough mode the select sever is unable to send messages
            directly to the client.
        """

        while self.valid():
            pass

        pass

    def close_socket( self ):

        super().close_socket()
        self.passthrough_socket.close()
