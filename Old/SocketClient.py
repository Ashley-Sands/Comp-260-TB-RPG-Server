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
        self.registered = False

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
                self.socket.send( msg_len )
                self.socket.send( msg_type )
                self.socket.send( msg_str.encode() )

                DEBUG.DEBUG.print( "Message sent", msg_str, "len", len(msg_str), "identity", chr(ord( message_obj.identity )) )
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
                self.valid( False )
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

    def close( self ):
        """Close down the socket and any running threads"""

        self.valid(False)
        self.socket.close()

        if self.inbound_thread.is_alive():
            self.inbound_thread.join()

        if self.outbound_thread is not None and self.outbound_thread.is_alive():
            self.outbound_thread.join()
