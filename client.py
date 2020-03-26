import datetime
import traceback
import queue as q
import threading
import time
import socket as py_socket
import DEBUG
from message import Message

# server
class Client:
    """ The protocol used by the socket
    <size of message [2 bytes]><identity char [1 byte]><message [size of message bytes]>
    max message size: 65,535 bytes (or chars)
    """

    MESSAGE_LEN_PACKET_SIZE = 2
    MESSAGE_TYPE_PACKET_SIZE = 1
    BYTE_ORDER = "big"

    def __init__(self, name, socket, client_key):

        # client
        self.name = name
        self.key = client_key

        # socket
        self.started = False
        self.socket = socket

        self._valid = self.socket is not None   # unsafe, use set and is valid functions
        self._closed = False

        self.received_queue = q.Queue()
        # this should not be used directly. Use 'que_message' function instead
        # as the que message function will spin up the send thread if its not already
        self._send_queue = q.Queue()

        self.inbound_thread = threading.Thread(target=self.inbound, args=(socket,))
        self.outbound_thread = threading.Thread(target=self.outbound, args=(socket,))

        self.thread_lock = threading.Lock()

        # game
        self._active_game = None            # use setter, getter and remove
        # values are reset via the remove game function
        self.game_player_id = -1
        self.game_player_is_ready = False

    def start(self):

        if self.inbound_thread.is_alive() or self.outbound_thread.is_alive():
            DEBUG.DEBUG.print("Error: can not start client, already alive")
            return

        self.started = True

        self.inbound_thread.start()
        self.outbound_thread.start()

    def is_valid(self, print_message=False):
        """ Thread safe method to see if the client is valid

        :param print_message: should a error message be displayed
        :return: True if the client is valid otherwise false
        """

        self.thread_lock.acquire()

        valid = self.socket is not None and self._valid and self.started

        self.thread_lock.release()

        if print_message and not valid:
            DEBUG.DEBUG.print("Error: Invalid Socket")

        return valid and not self._closed

    def set_is_valid( self, valid ):
        """ Thread safe method to set is vaild

        :param valid: is the socket vaild?
        """
        self.thread_lock.acquire()

        self._valid = valid

        self.thread_lock.release()

    def set_active_game( self, game ):
        """Sets the clients active and and adds the client to the game
        :return: True if added, otherwise false
        """
        if self._active_game is not None:
            DEBUG.DEBUG.print("Player can not join another game")
            return False

        self._active_game = game
        game.players[self.key] = self

        return True

    def get_active_game( self ):
        """Gets the players active game. None if there is no active game"""

        return self._active_game

    def remove_active_game( self, game ):
        """Removes the clinets active game and removes the client from the game
        :return: True if successfully remove, otherwise false
        """

        if game != self._active_game:
            return False

        game.players.remove( game )
        self._active_game = None
        self.game_player_id = -1
        self.game_player_is_ready = False

        return True


    def que_message( self, message_obj ):
        """Ques a message to be sent.
        If the send thread is not running this will start one
        :param message_obj:    An instance of the message class containing the message to be sent
        """
        # create the thread if we don't have one
        if self.outbound_thread is None:
            self.outbound_thread = threading.Thread( target=self.outbound, args=(self.socket,) )

        # que the message
        self._send_queue.put( message_obj )

        # if its not already start the thread to send messages
        if not self.outbound_thread.is_alive():
            self.outbound_thread.start()

    def inbound(self, socket):
        DEBUG.DEBUG.print("-starting inbound for ", self.key)
        # receive messages until it fails :/
        while self.is_valid():
            if not self.receive():
                return
            # time.sleep(0.5)

    def receive(self):
        """ Receives message putting it on top of the recived queue

        :return:    True if successful, false other wise.
        """

        if not self.is_valid(True):
            return False

        try:
            # receive the first couple of bytes for our message len
            data = self.socket.recv(self.MESSAGE_LEN_PACKET_SIZE)
            message_len = int.from_bytes(data, self.BYTE_ORDER)

            # if recv returns 0 bytes the socket has been disconnected
            # see https://docs.python.org/3.7/howto/sockets.html for more info
            # search "When a recv returns 0 bytes" on page.
            if len(data) == 0:
                self.set_is_valid( False )
                return False

            # receive the identity of the message
            data = self.socket.recv(self.MESSAGE_TYPE_PACKET_SIZE)
            message_id = chr(int.from_bytes(data, self.BYTE_ORDER))

            # receive the message
            message = self.socket.recv(message_len).decode("utf-8")
            DEBUG.DEBUG.print( "message received msg len:", message_len ,"msg:", message, "id", message_id, "from", self.name )

            # create the message instance
            message_obj = Message(self.key, message_id)
            message_obj.set_message( self.name, message )   # should this be the users key?

            self.received_queue.put(message_obj, block=True, timeout=None)

            #print( "message received msg len:", message_len ,"msg:", message, "id", message_id, "from", self.name )

            # self.timestamp_received = int(
            #    (datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1) ).total_seconds())

        except Exception as e:
            # traceback.print_last()
            DEBUG.DEBUG.print("Client ~line 175", e)
            self.set_is_valid( False )
            return False

        return True

    def outbound(self, socket):
        DEBUG.DEBUG.print("-starting outbound for", self.key)

        # send all messages in the queue
        while not self._send_queue.empty():
            if not self.send():
                return

        self.outbound_thread = None

    def send(self):
        """ Send message from the start of the send que

        :return:            true if a message was sent
        """

        if not self.is_valid(True):
            DEBUG.DEBUG.print( "Not Vaild" )
            return False

        message_obj = self._send_queue.get(block=True, timeout=None)

        message = message_obj.get_message()
        message_size = len(message).to_bytes(self.MESSAGE_LEN_PACKET_SIZE, self.BYTE_ORDER)
        message_id = ord(message_obj.identity).to_bytes(1, self.BYTE_ORDER)

        # check that the message is within the max message size
        if len(message) > pow(255, self.MESSAGE_LEN_PACKET_SIZE):
            DEBUG.DEBUG.print("Error: Message has exceeded the max message length.")
            return False

        try:
            self.socket.send( message_size )        # send the payload message size (2 bytes)
            self.socket.send( message_id )          # send the message object type  (1 byte )
            self.socket.send( message.encode() )    # send the message payload

        except Exception as e:
            DEBUG.DEBUG.print(e)
            self.set_is_valid( False )
            return False

        return True

    def close(self):

        if self._closed :
            return;

        # mark the client as invalid so the threads can exit once the sockets are closed
        self.set_is_valid( False )

        # close the connection
        self.socket.shutdown( py_socket.SHUT_RDWR )
        self.socket.close()  # close the socket once and for all, ready for GC

        # close any working threads
        if self.inbound_thread.is_alive():
            self.inbound_thread.join()

        if self.outbound_thread is not None and self.outbound_thread.is_alive():
            self.outbound_thread.join()

        self._closed = True
