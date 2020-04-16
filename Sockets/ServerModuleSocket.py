import Common.message as message
import Common.DEBUG as DEBUG
import Sockets.BaseSocket as BaseSocket
import queue
import threading
import time

class ServerModuleSocket( BaseSocket.BaseSocketClient ):

    def __init__(self, socket, sharded_received_queue=None):

        super().__init__( socket )

        self.client_nickname = "None"

        # set up the receive queue
        if sharded_received_queue is not None:
            self._receive_queue = sharded_received_queue
            self.sharded_queue = True
        else:   # leave in the old one queue per client for backwards capability
            self._receive_queue = queue.Queue()
            self.sharded_queue = False

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
        message_obj.times["time till sent"] = [time.time_ns(), 0]
        self._send_queue.put( message_obj )

        if self.outbound_thread is None:
            self.outbound_thread = threading.Thread( target=self.send_thread, args=(self.socket, ) )
            self.outbound_thread.start()


    def send_thread( self, socket ):

        DEBUG.LOGS.print( "starting send thread" )

        #while not self._send_queue.empty() and self.valid():
        while self.valid():
            # send message all messages in queue.

            message_obj = self._send_queue.get(block=True)

            if message_obj is None:
                DEBUG.LOGS.print("Received None message to send, exiting...")
                break

            message_obj.times[ "time till sent" ][1] = time.time_ns()
            message_obj.times["send_time"] = [time.time_ns(), 0]

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

            message_obj.times["send_time"][1] = time.time_ns()
            message_obj.times[list( message_obj.times.keys() )[0]][1] = time.time_ns()  # the fist time is always our in/out time
            message_obj.print_times()

        self.outbound_thread = None
        DEBUG.LOGS.print("Exiting outbound")

    def receive_message_pending( self ):
        """ returns true if theres a message in the que to be received.
            if using a sharded queue it will always return False
        :return:
        """
        return not self.sharded_queue and not self._receive_queue.empty()

    def receive_message( self ):
        """
            retrieves a message from the cue if one is available.
            if using a sharded queue it will always return None.
        """
        if not self.sharded_queue and not self._receive_queue.empty():
            return self._receive_queue.get()
        else:
            return None

    def receive_thread( self, socket ):

        while self.valid():
            # receive messages in three parts
            # Protocol layout.
            # message len (2 bytes) identity (1 byte) json message ( message len bytes)
            msg_len = 0
            start_receive = 0
            receive_id = 0
            convert = 0
            receive_msg = 0
            print_m = 0
            decode = 0
            try:
                msg_len_data = socket.recv( self.MESSAGE_LEN_PACKET_SIZE )
                start_receive = time.time_ns()

                # check there is data. if the connection was lost we will receive 0 bytes
                if len( msg_len_data ) == 0:
                    self.valid( False )
                    break

                msg_identity_data = socket.recv( self.MESSAGE_TYPE_PACKET_SIZE )
                receive_id = time.time_ns()
            except Exception as e:
                DEBUG.LOGS.print( "Could not receive data", e, message_type=DEBUG.LOGS.MSG_TYPE_ERROR )
                self.valid( False )
                return

            # convert our bytes to int and char
            msg_len = int.from_bytes( msg_len_data, self.BYTE_ORDER )
            msg_identity = chr( int.from_bytes( msg_identity_data, self.BYTE_ORDER ) )
            convert = time.time_ns()
            DEBUG.LOGS.print( "Received message len:",
                               msg_len, "Type:", msg_identity )
            print_m = time.time_ns()

            # receive the json message of msg_type with length msg_length
            try:
                json_str = self.socket.recv( msg_len )
                receive_msg = time.time_ns()
                json_str = json_str.decode( "utf-8" )
                decode = time.time_ns()
            except Exception as e:
                DEBUG.LOGS.print( "Could not receive data", e, message_type=DEBUG.LOGS.MSG_TYPE_ERROR )
                self.valid( False )
                break

            DEBUG.LOGS.print( "message ", json_str)

            message_obj = message.Message(msg_identity, self)
            message_obj.times["receive time"] = [start_receive, time.time_ns()]
            message_obj.set_from_json( "Client", json_str )
            message_obj.times["time till run"] = [time.time_ns(), 0]

            if (message_obj.times["receive time"][1] - message_obj.times["receive time"][0]) / 1000000.0 > 5:
                DEBUG.LOGS.print( "\nmessage length", msg_len,
                                  "\nreceive id", (receive_id - start_receive) / 1000000.0,
                                  "\nconvert", (convert - receive_id) / 1000000.0,
                                  "\ndebug print", (print_m - convert) / 1000000.0,
                                  "\nreceive body", (receive_msg-print_m) / 1000000.0,
                                  "\ndecode body", (decode-receive_msg) / 1000000.0,
                                  message_type=DEBUG.LOGS.MSG_TYPE_TIMES )

            self._receive_queue.put( message_obj )

    def safe_close( self ):
        """
            Closes the connection once the send que is empty
            Blocks until connection can close
        """

        DEBUG.LOGS.print("### Pre safe close", self.valid(), not self._send_queue.empty(), self.outbound_thread is not None)

        while self.valid() and not self._send_queue.empty():
            pass # wait until the outbound thread stops

        self.close()

        DEBUG.LOGS.print("########## Safely Closed ", self._client_db_id)

    def close( self ):

        # we must put something in the send que to unblock it :)
        # and allow the threads to join
        self._send_queue.put( None )
        super().close()