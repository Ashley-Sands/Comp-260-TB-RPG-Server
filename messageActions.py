from StaticActions import StaticActions
import message as msg
from constants import *

class MessageAction:

    def __init__( self, game_inst, send_message_func, get_client_list_func, get_client_func, get_games_func ):
        # self.game_inst = game_inst
        self.send_message = send_message_func
        self.get_client_list = get_client_list_func
        self.get_client = get_client_func
        self.get_games = get_games_func

    def run( self, message_obj ):
        """

        :param message_obj: instance of messages containing the data
        :return: None
        """
        pass


class Action_SendMessage( MessageAction ):  # m

    def run( self, message_obj ):

        clients = self.get_client_list( [message_obj.from_client_key] )
        message_obj.to_clients = clients

        self.send_message( message_obj )
        print("Sending message")


class Action_ClientIdentity( MessageAction ):   # i

    def run( self, message_obj ):
        client = self.get_client( message_obj.from_client_key )
        client.name = message_obj.message["nickname"]

        # notify the other players that they have connected
        # TODO: this might get dropped when theres more than one room
        StaticActions.send_client_status( True, "", client.key, SERVER_NAME,
                                          self.get_client_list, self.send_message )

        StaticActions.send_server_status(True, "", client.key, SERVER_NAME,
                                         self.send_message)


class Action_status( MessageAction ):

    TYPE_NONE   = -1
    TYPE_SERVER = 0
    TYPE_CLIENT = 1
    TYPE_GAME   = 2

    def run ( self, messageObj ):
        pass

class Action_GamesRequest( MessageAction ): # g

    def run( self, message_obj ):

        # fill in the game names and slots data and send the class back to the client
        games = self.get_games()

        game_names = []
        game_slots = []

        for g in games:
            game_names.append( g.game_name )
            game_slots.append( str(g.max_players - g.get_player_count()) + " of " + str(g.max_players) )

        message_obj.to_clients = [message_obj.from_client_key]
        message_obj.message["available_games"] = game_names
        message_obj.message["available_slots"] = game_slots

        self.send_message( message_obj )

class Action_JoinGameRequest( MessageAction ): # j

    def run( self, message_obj ):

        games = self.get_games(False)

        for g in games:
            if g.game_name == message_obj["match_name"]:
                if g.can_join():
                    # TODO: add the player to the game...
                    # let the player knows every thing is ok
                    StaticActions.send_game_status(True, "", message_obj.from_client_key,
                                                   SERVER_NAME, self.send_message)
                else:
                    StaticActions.send_game_status( False, self.get_error_message(g),
                                                    message_obj.from_client_key,
                                                    SERVER_NAME, self.send_message )
                return

            # so its not ok, the game is no longer available
            StaticActions.send_game_status( False, "Game does not exist!", message_obj.from_client_key,
                                            SERVER_NAME, self.send_message )


    def get_error_message( self, game ):

        err_msg = ""
        if game.game_active:
            err_msg = "Game has already started"
        elif game.get_available_slots() < 1:
            err_msg = "Server is full"

        return err_msg
