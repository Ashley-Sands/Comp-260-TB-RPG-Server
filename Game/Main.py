import  threading
import time

class Main:

    def __init__(self):

        self._can_join = True
        self.game_active = False

        self.start_in = 300         # start in 5 min
        self.starts_at = 0;

        self.start_thread = threading.Thread(target=self.start_game)
        self.start_thread.start()
        self.thread_lock = threading.Lock()

        self.game_name = "default"
        self.map_name = "default"

        self.max_players = 4

        self.players = {}


    def get_player_count( self ):
        """Thread safe method to get player Count"""

        self.thread_lock.acquire()

        player_count = len(self.players)

        self.thread_lock.release()

        return player_count

    def get_player_names( self ):

        p_names = []

        for p in self.players:
            p_names.append( self.players[p].name )

        return p_names

    def get_player_keys( self ):

        return [*self.players]

    def get_available_slots( self ):

        return self.max_players - self.get_player_count()

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

    def get_time_till_start( self ):

        self.thread_lock.acquire()
        remaining_time = self.starts_at - time.time()
        self.thread_lock.release()

        return remaining_time

    # threaded
    def start_game( self ):

        can_start = False
        start_delay = self.start_in

        while not can_start:

            self.starts_at = time.time() + start_delay
            time.sleep( start_delay )     # sleep until its time to start the game

            if self.get_player_count() > 1:
                can_start = True

