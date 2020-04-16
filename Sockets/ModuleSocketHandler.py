import Common.DEBUG as DEBUG
import socket
import time
import queue
import threading
import Common.constants as constants
import Sockets.SocketHandler as SocketHandler


class ModuleSocketHandler( SocketHandler.SocketHandler ):

    def __init__(self, ip, port, max_conn, module_socket):

        super().__init__(ip, port, max_conn, module_socket)

        self.inbound_message = queue.Queue()    # que of message objects
        self.process_message_thread = threading.Thread(target=self.process_inbound_messages)

    def start( self ):

        super().start()

        # start the inbound message thread.
        self.process_message_thread.start()

    def new_connection( self, client_socket ):

        return self.socket_client_class( client_socket, self.inbound_message )

    def process_inbound_messages( self ):

        while self.valid:

            message_obj = self.inbound_message.get(block=True, timeout=None)

            if message_obj is None:
                DEBUG.LOGS.print("Received None message, exiting process inbound message")
                break

            message_obj["time till run"][1] = time.time_ns()
            message_obj.measure_time("run action", message_obj.run_action() )

    def close( self ):

        super().close()

        # queue a none to unblock the inbound message que
        # and wait for the thread to join
        self.inbound_message.put(None)

        if self.process_message_thread.is_alive():
            self.process_message_thread.join()

        DEBUG.LOGS.print( "Process message thread closed successfully" )
