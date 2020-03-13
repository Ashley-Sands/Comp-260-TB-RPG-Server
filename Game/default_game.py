import time
import message as msg
import constants

class DefaultGame:

    def __init__(self, send_message_func):

        self.game_name = "default"
        self.map_name = "default"

        self.playerId = {}  # key: player id, value: player_key
        self.ready = {}     # Are the players ready Key: player id value True or False

        self.current_player = 0
        self.max_players = 4

        self.max_time = 15

        self.send_message = send_message_func


    def run( self ):

        print("sleeping for ", self.max_time)
        time.sleep(self.max_time)
        print("Who awakens me!")
        # get the next player id
        # taking into account that a player might of disconnected
        for i in range(self.max_players):
            self.current_player += 1

            if self.current_player > self.max_players:
                self.current_player = 0
            if self.current_player in self.playerId:
                break

        changePlayer = msg.Message(constants.SERVER_NAME, 'C')
        changePlayer.message = changePlayer.new_message(constants.SERVER_NAME,
                                                        self.current_player,
                                                        self.max_time )

        changePlayer.to_clients = list( self.playerId.values() )

        self.send_message( changePlayer )