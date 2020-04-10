import Common.message as message
import Common.DEBUG as DEBUG
import Sockets.BaseSocket as BaseSocket
import queue
import threading
import time

class ServerModuleSocket( BaseSocket.BaseSocketClient ):

    def __init__(self, socket):

        super().__init__( socket )

        self.client_nickname = "None"

        self._receive_queue = queue.Queue()
        self._send_queue = queue.Queue()

    def start( self ):

        if self._started:
            return

        self.inbound_thread = threading.Thread( target=self.receive_thread, args=(self.socket, ) )
        self.inbound_thread.start()

        super().start()

    def send_message( self, message_obj ):

        # cue the message and if the send thread is not running start it :)
        # discard if its marked with ERR
        if message_obj.ERR:
            return

        self._send_queue.put( message_obj )

        if self.outbound_thread is None:
            self.outbound_thread = threading.Thread( target=self.send_thread, args=(self.socket, ) )
            self.outbound_thread.start()


    def send_thread( self, socket ):

        DEBUG.LOGS.print( "starting send thread" )

        while not self._send_queue.empty() and self.valid():
            # send message all messages in queue.

            message_obj = self._send_queue.get()
            msg_str = message_obj.get_json()

            # convert the message len and identity char to bytes
            msg_len = len( msg_str ).to_bytes( self.MESSAGE_LEN_PACKET_SIZE, self.BYTE_ORDER )
            msg_type = ord( message_obj.identity ).to_bytes( self.MESSAGE_TYPE_PACKET_SIZE, self.BYTE_ORDER )

            # check that the message is within the max message size
            if len( msg_str ) > pow( 255, self.MESSAGE_LEN_PACKET_SIZE ):
                DEBUG.LOGS.print( "Message has exceeded the max message length.",
                                  message_type=DEBUG.LOGS.MSG_TYPE_ERROR )
                return

            # attempt to receive message
            try:
                socket.send( msg_len + msg_type + msg_str.encode() )

                DEBUG.LOGS.print( "Message sent", msg_str, "len", len( msg_str ),
                                  "identity", chr( ord( message_obj.identity ) ) )

            except Exception as e:
                DEBUG.LOGS.print( "Could not send data:", e,
                                  message_type=DEBUG.LOGS.MSG_TYPE_ERROR )
                self.valid( False )

        self.outbound_thread = None
        DEBUG.LOGS.print("Exiting outbound")

    def receive_message_pending( self ):
        return not self._receive_queue.empty()

    def receive_message( self ):

        if not self._receive_queue.empty():
            return self._receive_queue.get()
        else:
            return None

    def receive_thread( self, socket ):

        while self.valid():
            # receive messages in three parts
            # Protocol layout.
            # message len (2 bytes) identity (1 byte) json message ( message len bytes)

            try:
                msg_len_data = socket.recv( self.MESSAGE_LEN_PACKET_SIZE )

                # check there is data. if the connection was lost we will receive 0 bytes
                if len( msg_len_data ) == 0:
                    self.valid( False )
                    break

                msg_identity_data = socket.recv( self.MESSAGE_TYPE_PACKET_SIZE )
            except Exception as e:
                DEBUG.LOGS.print( "Could not receive data", e, message_type=DEBUG.LOGS.MSG_TYPE_ERROR )
                self.valid( False )
                return

            # convert our bytes to int and char
            msg_len = int.from_bytes( msg_len_data, self.BYTE_ORDER )
            msg_identity = chr( int.from_bytes( msg_identity_data, self.BYTE_ORDER ) )

            DEBUG.LOGS.print( "Received message len:",
                               msg_len, "Type:", msg_identity )

            # receive the json message of msg_type with length msg_length
            try:
                json_str = self.socket.recv( msg_len ).decode( "utf-8" )
            except Exception as e:
                DEBUG.LOGS.print( "Could not receive data", e, message_type=DEBUG.LOGS.MSG_TYPE_ERROR )
                self.valid( False )
                break

            DEBUG.LOGS.print( "message ", json_str)

            message_obj = message.Message(msg_identity, self)
            message_obj.set_from_json( "Client", json_str )

            self._receive_queue.put( message_obj )

    def safe_close( self ):
        """
            Closes the connection once the send que is empty
            Blocks until connection can close
        """

        DEBUG.LOGS.print("### Pre safe close", self.valid(), not self._send_queue.empty(), self.outbound_thread is not None)
        while ( self.valid() and not self._send_queue.empty() ) or self.outbound_thread is not None:
            pass # wait until the outbound thread stops

        self.close()
        DEBUG.LOGS.print("########## Safely Closed ", self._client_db_id)
