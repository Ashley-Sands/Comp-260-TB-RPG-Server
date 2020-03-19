# treat as if this is a static class
class MessageTypes:
    # All messages types should have a from client param

    @staticmethod
    def message( from_client, message ):                        # m
        """Basic message to all users"""
        return locals()

    @staticmethod
    def client_identity( from_client, nickname, reg_key ):       # i
        """Request to the client for there identity
        The server sends an empty client_identity for client to fill in and return back to the server
        to complete registration.
        :param from_client:     The client that sent the message (SERVER)
        :param nickname:        the nickname of the client (set on the clients end)
        :param reg_key:         The reg_key is only required to re-join
        """
        return locals()

    @staticmethod
    def client_registered(from_client, ok, client_id, reg_key):     # r
        """Notifies the client that they have successfully registered"""
        return locals()

#-------------------------
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
    def current_lobby_request( from_client, lobby_ids, level_names, min_players, max_players, current_players ):      # g
        """ sent from the server to the client contating the all the available games :)
        if this is received by the server a new one will be sent back to the client  :D

        :param from_client:     SERVER
        :param lobby_ids:       List of games available to play
        :param level_names:     List of level names
        :param min_players:     List of min players
        :param max_players:     List of max players
        :param current_players: List of current_players
        """
        return locals()

    @staticmethod
    def join_lobby_request( from_client, lobby_id, host, port ):  # j
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
    def game_info( from_client, game_name, players, min_players, max_players, starts_in ):
        """ game data such as current players ect...
        :param game_name:   name of name that info belongs to
        :param players:     list of current players
        :param min_players: min number of players allowed on the server
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
