import message
import messageActions
# these are actions that are not trigger by send/receiving messages


class StaticActions:

    @staticmethod
    def send_client_status( ok, msg, client_key, from_name, get_client_list_func, send_message_func, game=None ):
        """ Send the status of a client to all other clients

        :param ok:                      has the user connected (True) or disconnected (False)
        :param msg:                 the message to send other clients (if required)
        :param client_key:              The key of the client who's status this is
        :param from_name:               who has sent the send ie SERVER
        :param get_client_list_func:    function to get a list of clients
        :param send_message_func:       function to send message
        :param game:                    the game clients belong to
        :return:                        None
        """
        status_type = messageActions.Action_status.TYPE_CLIENT

        new_client_message = message.Message( client_key, 's' )
        new_message = new_client_message.new_message( from_name, status_type, ok, msg )
        new_client_message.message = new_message
        new_client_message.to_clients = get_client_list_func( [ client_key ], game )

        send_message_func( new_client_message )

    @staticmethod
    def send_server_status( ok, msg, client_key, from_name, send_message_func ):
        """ Send the status of the server to a single client

        :param ok:                      has the user connected (True) or disconnected (False)
        :param msg:                     the message to send other clients (if required)
        :param client_key:              The key of the client to send the message to
        :param from_name:               who has sent the send ie SERVER
        :param send_message_func:       function to send message
        :return:                        None
        """

        status_type = messageActions.Action_status.TYPE_SERVER

        new_client_message = message.Message( client_key, 's' )
        new_message = new_client_message.new_message( from_name, status_type, ok, msg )
        new_client_message.message = new_message
        new_client_message.to_clients = [ client_key ]

        send_message_func( new_client_message )

    @staticmethod
    def send_game_status(ok, msg, client_key, from_name, send_message_func ):
        """ Send the status of a game to a single clients

        :param ok:                      has the user connected (True) or disconnected (False)
        :param msg:                     the message to send other clients (if required)
        :param client_key:              The key of the client to send the message to
        :param from_name:               who has sent the send ie SERVER
        :param send_message_func:       function to send message
        :return:                        None
        """

        status_type = messageActions.Action_status.TYPE_GAME

        new_client_message = message.Message( client_key, 's' )
        new_message = new_client_message.new_message( from_name, status_type, ok, msg )
        new_client_message.message = new_message
        new_client_message.to_clients = [ client_key ]

        send_message_func( new_client_message )

    @staticmethod
    def send_game_info( game, client_key, from_name, send_message_func ):
        """ sends the game info to client key

        :param game:                the game to get data from
        :param client_key:          the client key to send to
        :param from_name:           the client that the message came from ie SERVER
        :param send_message_func:   the send message function
        :return:                    None
        """

        game_info = message.Message( client_key, 'd' )
        new_message = game_info.new_message(from_name, game.game_name, game.get_player_names(),
                                            game.max_players, game.get_time_till_start())
        game_info.message = new_message
        game_info.to_clients = [ client_key ]

        send_message_func( game_info )
