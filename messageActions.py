from StaticActions import StaticActions

class MessageAction:

    def __init__( self, game_inst, send_message_func, get_client_list_func, get_client_func ):
        self.game_inst = game_inst
        self.send_message = send_message_func
        self.get_client_list = get_client_list_func
        self.get_client = get_client_func

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
