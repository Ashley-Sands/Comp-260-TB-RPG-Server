import  threading
import time
import message
import constants
import random

class Main:

    def __init__(self, send_message_func):

        self._can_join = True
        self.game_active = False

        self.start_in = 60  # 300         # start in 5 min
        self.starts_at = 0;

        self.start_thread = threading.Thread(target=self.start_game)
        self.start_thread.start()
        self.thread_lock = threading.Lock()

        self.game_name = "default"
        self.map_name = "default"

        self.max_players = 4

        self.players = {}   # clients that are in the game
        self.playerId = {}  # key: player id, value: player_key

        self.send_message = send_message_func

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

    def player_joined( self, player_key, player_id ):
        """ Adds the player to player id. once all players have been added
        the game can become active

        :param player_key:      the key of the player
        :param player_id:       the players id in the game
        :return:
        """
        self.playerId[player_id] = player_key

        if len( self.playerId ) == len( self.players ):
            # update the clients with the full player list, ready to begin.
            pre_start_message = message.Message(player_key, 'P')
            pre_start_message.message = pre_start_message.new_message(constants.SERVER_NAME, [*self.playerId], list(self.playerId))
            pre_start_message.to_clients = [*self.players]

            self.send_message(pre_start_message) # now we wait for the player to ok. then we begin :D


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

        self._can_join = False

        # get player ids so we can select them at random
        player_ids = [*range(len(self.players))]

        for p in self.players:
            rand_id = random.choice(player_ids)
            player_ids.remove(rand_id)

            launch_game = message.Message(constants.SERVER_NAME, 'b')
            launch_game.message = launch_game.new_message(constants.SERVER_NAME, rand_id)
            launch_game.to_clients = [p]


            self.send_message( launch_game )

