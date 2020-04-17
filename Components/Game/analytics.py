import Common.database as database
import Common.DEBUG as DEBUG
import threading
import queue
import Common.database
import time

class Analytics:

    def __init__( self ):

        self.queue = queue.Queue()
        self.running = True
        self.database = database.Database()

        self.thread_lock = threading.Lock()
        self.update_thread = threading.Thread( target=self.update )
        self.update_thread.start()

    def __del__(self):
        self.stop()

    def update( self ):

        while self.running:

            if self.queue.empty():
                time.sleep(0.1)
                continue
            DEBUG.LOGS.print( "Update Analytics" )

            player_id, reg_key, message_obj = self.queue.get( )
            data = message_obj.get_json()
            identity = message_obj.identity

            # get the players current game and level id.
            lobby_id = self.database.get_client_lobby( reg_key )
            lobby_info = self.database.get_lobby_row( lobby_id )
            level_id = lobby_id
            game_count = lobby_info[3]

            self.database.add_analytic_data( identity, data, player_id, lobby_id,
                                             game_count, level_id, int(time.time()) )

    def add_data( self, message_obj ):
        """

        :param connection:  Must be a ServerGameSocket
        :param data:        ?
        :return:
        """
        DEBUG.LOGS.print("New Analytics")
        connection = message_obj.from_connection
        self.queue.put( (connection.player_id, connection.get_client_key()[1], message_obj) )

    def stop( self ):

        self.thread_lock.acquire()
        self.running = False
        self.thread_lock.release()

        if self.update_thread.is_alive():
            self.update_thread.join()

        DEBUG.LOGS.print( "Analytics Stopped" )
