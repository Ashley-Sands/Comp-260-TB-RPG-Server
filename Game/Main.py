import  threading
import time
import message
import constants
import random
from Game.default_game import DefaultGame
import StaticActions
import messageActions
import DEBUG


class Main:

    def __init__(self, send_message_func):

        self.send_message = send_message_func

        self._can_join = True
        self._game_active = False
        self._valid = True

        self.start_in = 30  # 300         # start in 5 min
        self.starts_at = 0

        self.game = DefaultGame( send_message_func )

        self.players = {}   # clients that are in the game

        self.thread_lock = threading.Lock()

        self.lobby_thread = threading.Thread(target=self.update_lobby)
        self.lobby_thread.start()
        self.game_thread = threading.Thread(target=self.update_game)


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

        return self.game.max_players - self.get_player_count()

    def set_is_valid( self, valid ):

        self.thread_lock.acquire()
        self._valid = valid
        self.thread_lock.release()

    def is_valid( self ):
        return self._valid

    def can_join( self ):

        return self._can_join and not self.game_active() and self.get_player_count() < self.game.max_players and self.is_valid()

    def game_active( self ):

        self.thread_lock.acquire()
        active = self._game_active
        self.thread_lock.release()

        return active

    def set_game_active( self, active ):

        self.thread_lock.acquire()
        self._game_active = active
        self.thread_lock.release()

    def add_player( self, client):
        """Adds a client to the players list

        :return:    true if successfully joined otherwise false
        """
        if not self.can_join():
            return False

        self.players[client.key] = client

        return True

    def remove_player( self, client ):
        """Removes a client to the players list

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
        self.game.playerId[player_id] = player_key
        self.players[ player_key ].game_player_id = player_id

        if len( self.game.playerId ) == len( self.players ):
            # update the clients with the full player list, ready to begin.
            pre_start_message = message.Message(player_key, 'P')
            pre_start_message.message = pre_start_message.new_message(constants.SERVER_NAME, [*self.game.playerId], list(self.game.playerId.values()))
            pre_start_message.to_clients = [*self.players]

            self.send_message(pre_start_message) # now we wait for the player to ok. then we begin :D

    def ready_player( self, player_key, ready ):
        """Readies the player to start the game!"""

        self.game.ready[ player_key ] = ready

        # once we have a responce from all the players
        # the game can start as long as
        # every ones status is OK :)
        ok = len(self.game.ready) == len(self.game.playerId)
        if ok:
            for r in self.game.ready:
                if not self.game.ready[r]:
                    ok = False
                    break   # todo: find out why

        if ok:  # so we good :)
            self.set_game_active(True)
            start_game_msg = message.Message(constants.SERVER_NAME, 'S')
            start_game_msg.message = start_game_msg.new_message(constants.SERVER_NAME, True)
            start_game_msg.to_clients = list( self.game.playerId.values() )  # we use the playerId as they have been confirmed and joined!

            self.send_message( start_game_msg )
            self.game_thread.start()


    def get_time_till_start( self ):

        self.thread_lock.acquire()
        remaining_time = self.starts_at - time.time()
        self.thread_lock.release()

        return remaining_time

    # threaded
    def update_lobby( self ):

        # wait for the lobby to launch into the game
        can_start = False
        start_delay = self.start_in

        while not can_start:

            # sleep until there are enough players to start
            while self.get_player_count() < self.game.min_players:
                time.sleep(5)   # TODO: add min players to game info protocol

            self.starts_at = time.time() + start_delay

            # update any connected players, that we're going to wait again
            StaticActions.StaticActions.send_game_info_to_all( self, self.send_message )

            time.sleep( start_delay )     # sleep until its time to start the game

            if self.get_player_count() >= self.game.min_players:  # there must be at least 2 players
                can_start = True

        # prevent more players from joining
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

    def update_game( self ):

        DEBUG.DEBUG.print("Starting game", self.game.game_name)

        while self.game_active():
            self.game.run()

            time.sleep(0.016)   # update ~60 times a second

            # check there are still players
            if self.get_player_count() < self.game.min_players:
                game_error = message.Message(constants.SERVER_NAME, 's')
                game_error.message = game_error.new_message( constants.SERVER_NAME,
                                                             messageActions.Action_status.TYPE_SERVER,
                                                             False, "ERROR: Not enough players to continue game...")
                game_error.to_clients = [*self.players]
                self.send_message( game_error )

                self.set_is_valid(False)    # mark as invalid so it can get reset

                return
