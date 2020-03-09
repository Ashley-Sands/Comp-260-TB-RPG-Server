from StaticActions import StaticActions
import message as msg

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


class Action_SendMessage( MessageAction ):

    def run( self, message_obj ):

        clients = self.get_client_list( [message_obj.from_client_key] )
        message_obj.to_clients = clients

        self.send_message( message_obj )
        print("Sending message")


class Action_ClientIdentity( MessageAction ):

    def run( self, message_obj ):
        client = self.get_client( message_obj.from_client_key )
        client.name = message_obj.message["nickname"]

        # notify the other players that they have connected
        # TODO: this might get dropped when theres more than one room
        StaticActions.send_client_status( True, client.key, client.name,
                                          self.get_client_list, self.send_message )

        status_message = msg.Message( client.key, 'S')
        status_message.to_clients = [client.key]
        status_message.message = status_message.new_message("SERVER", True);
        self.send_message(status_message)


class Action_GamesRequest( MessageAction ):

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
