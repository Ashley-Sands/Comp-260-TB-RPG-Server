import Common.DEBUG as DEBUG
import threading
import Common.constants as constants
import socket

class BaseSocketClient:
    """Socket clients are used handle the clients inbound/outbound messages."""

    MESSAGE_LEN_PACKET_SIZE = 2  # bytes
    MESSAGE_TYPE_PACKET_SIZE = 1  # byte
    BYTE_ORDER = "big"

    def __init__( self, socket ):

        self.socket = socket
        # might be worth putting theses in the base class :)

        self._client_db_id = ""
        self._reg_key = ""

        self.thread_lock = threading.Lock()
        self.inbound_thread = None
        self.outbound_thread = None

        self._started = False
        self._valid = True

    def start( self ):
        """
        Called to allow the inbound and outbound thread to be fired up
        Override to define how the threads should be started
        """

        self._started = True

    def valid( self, is_valid=None ):
        """
        Thread safe method tp get and set _valid
        If is_valid is None, it is not set
        """

        self.thread_lock.acquire()

        if is_valid is not None:
            self._valid = is_valid

        is_valid = self._valid

        self.thread_lock.release()

        return is_valid

    def from_name( self ):
        """ What should be displayed as from name when sending message from this socket.
            By default this is 'SERVER' (constants.SERVER_NAME)
        """
        return constants.SERVER_NAME

    def set_client_key( self, client_db_id, reg_key ):
        """Thread safe method to set the client id and reg key"""

        self.thread_lock.acquire()
        self._client_db_id = client_db_id
        self._reg_key = reg_key
        self.thread_lock.release()

    def get_client_key( self ):
        """Thread safe method to get the clients db id and reg key
        :return: tuple ((int)id, (string)key)
        """

        self.thread_lock.acquire()

        cid = self._client_db_id
        rkey = self._reg_key

        self.thread_lock.release()

        return cid, rkey

    def close_socket( self ):
        try:
            self.socket.shutdown( socket.SHUT_RDWR )
        except:
            pass

        try:
            self.socket.close()
        except Exception as e:
            DEBUG.LOGS.print("Bad socket: ", e, DEBUG.LOGS.MSG_TYPE_WARNING)

    def join_threads( self ):
        """
            joins both inbound and outbound threads back onto the main if needed.
            Be sure to of called closed_socket, to allow the sockets to exit.
        """

        if self.inbound_thread.is_alive():
            self.inbound_thread.join()

        if self.outbound_thread is not None and self.outbound_thread.is_alive():
            self.outbound_thread.join()


    def close( self ):
        """
            Closes the sockets and joins the threads asap (ignoring any queued tasks)
            Override close_socket and join_threads to extend
        """
        self.valid( False )

        self.close_socket()
        self.join_threads()

        DEBUG.LOGS.print( "Client Socket Closed" )
