# treat as if this is a static class
class MessageTypes:
    # All messages types should have a from client param

    @staticmethod
    def message( from_client, message ):                # m
        """Basic message to all users"""
        return locals()

    @staticmethod
    def client_identity( from_client, nickname ):       # i
        """Request to the client for there identity"""
        return locals()

    @staticmethod
    def status( from_client, status_type, ok, message ):        # s
        """Basic message for client connect/dissconnect
        connected is true, otherwise false
        :param from_client: the client that the message was received from
        :param status_type: type of status, See Action_status for constance status types
        :param ok:          is everything ok?
        :param message:     if not what up?
        """
        return locals()

    @staticmethod
    def game_request( from_client, available_games, available_slots ):      # g
        """ list of games request

        :param from_client:
        :param available_games: List of games available to play
        :param available_slots: the amount of slots available in game
        """
        return locals()

    @staticmethod
    def join_lobby_request( from_client, match_name ):
        """ a request to join a game

        :param match_name: name of game
        :return: as dict
        """
        return locals()

    @staticmethod
    def leave_game_request(from_client):
        """Request to leave game"""
        return locals()

    @staticmethod
    def game_info( from_client, game_name, players, max_players, starts_in ):
        """ game data such as current players ect...
        :param game_name:   name of name that info belongs to
        :param players:     list of current players
        :param max_players: max number of players allowed on the server
        :param starts_in:   the amount of time until the game starts
        :return:
        """
        return locals()

    @staticmethod
    def launch_game( from_client, player_id):
        """

        :param from_client:     SERVER
        :param player_id:       the ID that the game will use
        :return:
        """
        return locals()

    @staticmethod
    def joined_game ( from_client, player_id ):
        """

        :param from_client:
        :param player_name:
        :param player_id:
        :return:
        """
        return locals()

    @staticmethod
    def pre_start_game( from_client, player_ids, player_names ):
        """

        :param from_client:
        :param player_ids:
        :param player_names:
        :return:
        """
        return locals()

    @staticmethod
    def start_game( from_client, ok ):
        """

        :param from_client:
        :param ok:
        :return:
        """
        return locals()
