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
    def client_status( from_client, connected ):        # s
        """Basic message for client connect/dissconnect
        connected is true, otherwise false
        """
        return locals()

    @staticmethod
    def server_status( from_client, ok ):               # S
        """Basic message for client connect/dissconnect
        connected is true, otherwise false
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
    def join_game_request( match_name ):
        """ a request to join a game

        :param match_name: name of game
        :return: as dict
        """
        return locals()

    @staticmethod
    def leave_game_request():
        """Request to leave game"""
        return {}

    @staticmethod
    def game_status( ok, message ):
        """game status of the clients current game

        :param ok:          is the game ok?
        :param message:     if not why?
        :return:
        """
        return locals()

    @staticmethod
    def game_data( players ):
        """ game data such as current players ect...

        :param players:     list of current players
        :return:
        """
        return locals()
