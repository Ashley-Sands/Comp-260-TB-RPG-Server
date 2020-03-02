import datetime
import queue as q
import threading
import time
import socket as py_socket

# server
class Client:
    """ The protocol used by the socket
    <size of message [2 bytes]><identity char [1 byte]><message [size of message bytes]>
    max message size: 65,535 bytes (or chars)
    """

    MESSAGE_LEN_PACKET_SIZE = 2
    BYTE_ORDER = "big"

    def __init__(self, name, socket):

        self.name = name
        self.socket = socket
        self.started = False

        self._valid = self.socket is not None   # unsafe, use set and is valid functions
        self.received_queue = q.Queue()
        # this should not be used directly. Use 'que_message' function instead
        self._send_queue = q.Queue()

        self.inbound_thread = threading.Thread(target=self.inbound, args=(socket,))
        self.outbound_thread = threading.Thread(target=self.outbound, args=(socket,))

        self.thread_lock = threading.Lock()

    def start(self):

        if self.inbound_thread.is_alive() or self.outbound_thread.is_alive():
            print("Error: can not start client, already alive")
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
            print("Error: Invalid Socket")

        return valid

    def set_is_valid( self, valid ):
        """ Thread safe method to set is vaild

        :param valid: is the socket vaild?
        """
        self.thread_lock.acquire()

        self._valid = valid

        self.thread_lock.release()

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
        print("-starting inbound")
        # receive messages until it fails :/
        while self.is_valid():
            if not self.receive():
                return
            time.sleep(0.5)

    def receive(self):
        """ Receives message putting it on top of the recived queue

        :return:    True if successful, false other wise.
        """

        if not self.is_valid(True):
            return False

        try:

            # receive the first bytes couple of bytes for our message len
            data = self.socket.recv(self.MESSAGE_LEN_PACKET_SIZE)
            message_len = int.from_bytes(data, self.BYTE_ORDER)

            # if recv returns 0 bytes the socket has been disconnected
            # see https://docs.python.org/3.7/howto/sockets.html for more info
            # search "When a recv returns 0 bytes" on page.
            if len(data) == 0:
                self.set_is_valid( False )
                return False

            # receive the message
            message = self.socket.recv(message_len).decode("utf-8")
            self.received_queue.put(message, block=True, timeout=None)

            # self.timestamp_received = int(
            #    (datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1) ).total_seconds())

        except Exception as e:
            print(e)
            self.set_is_valid( False )
            return False

        return True

    def outbound(self, socket):
        print("-starting outbound")

        # send all messages in the queue
        while not self._send_queue.empty():
            if not self.send():
                return

    def send(self):
        """ Send message from the start of the send que

        :return:            true if a message was sent
        """

        if not self.is_valid(True):
            return False

        message = self.send_queue.get(block=True, timeout=None)

        # check that the message is within the max message size
        if len(message) > pow(255, self.MESSAGE_LEN_PACKET_SIZE):
            print("Error: Message has exceeded the max message length.")
            return False

        message_length = len(message).to_bytes(self.MESSAGE_LEN_PACKET_SIZE, self.BYTE_ORDER)

        try:
            self.socket.send( message_length )
            self.socket.send( message.encode() )
        except Exception as e:
            print(e)
            self.set_is_valid( False )
            return False

        return True

    def close(self):
        # mark the client as invalid so the threads can exit once the sockets are closed
        self.set_is_valid( False )

        # close the connection
        self.socket.shutdown( py_socket.SHUT_RDWR )
        self.socket.close()  # close the socket once and for all, ready for GC

        # close any working threads
        if self.inbound_thread.is_alive():
            self.inbound_thread.join()

        if self.outbound_thread.is_alive():
            self.outbound_thread.join()
