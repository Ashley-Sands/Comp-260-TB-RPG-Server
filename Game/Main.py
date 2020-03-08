import  threading
import time

class Main:

    def __init__(self):

        self._can_join = True
        self.game_active = False

        self.start_in = 300         # start in 5 min

        self.start_thread = threading.Thread(target=self.start_game)
        self.start_thread.start()
        self.thread_lock = threading.Lock()

        self.map_name = "default"

        self.max_players = 4

        self.players = {}


    def get_player_count( self ):
        """Thread safe method to get player Count"""

        self.thread_lock.acquire()

        player_count = len(self.players)

        self.thread_lock.release()

        return player_count

    def can_join( self ):

        return self._can_join and not self.game_active and self.get_player_count() < self.max_players

    def add_player( self, client):
        """Adds a client to the players list

        :return:    true if successfully joined otherwise false
        """
        if not self.can_join():
            return False

        self.player[client.key] = client

        return True

    def remove_player( self, client ):
        """Adds a client to the players list

        :return:    true if successfully removed otherwise false
        """

        if client.key not in self.players:
            return False

        del self.players[ client.key ]

        return True

    # threaded
    def start_game( self ):

        can_start = False

        while not can_start:

            time.sleep( self.start_in )     # sleep until its time to start the game

            if self.get_player_count() > 1:
                can_start = True

