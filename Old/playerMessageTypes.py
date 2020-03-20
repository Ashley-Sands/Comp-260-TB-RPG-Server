import message as msg
from constants import *

class PlayerMessageTypes:

    @staticmethod
    def change_player( from_id, player_id, turn_len):
        """

        :param from_id:         SERVER
        :param player_id:       change to player id
        :param turn_len:     length of time the player gets
        :return:
        """
        return locals()

    @staticmethod
    def move_player(from_id, player_id, x, y, z):
        """

        :param from_id:
        :param player_id:
        :param x:
        :param y:
        :param z:
        :return:
        """

        return locals()