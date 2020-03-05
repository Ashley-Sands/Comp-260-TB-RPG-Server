
class MessageAction:

    def __init__( self, game_inst, send_message_func, get_client_list_func, get_client_func ):
        self.game_inst = game_inst
        self.send_message = send_message_func
        self.get_client_list = get_client_list_func
        self.get_client = get_client_func

    def run( self, message_obj ):
        """

        :param message_obj:
        :return:
        """
        pass


class Action_SendMessage( MessageAction ):

    def run( self, message_obj ):

        clients = self.get_client_list( [message_obj.from_client_id] )
        message_obj.to_clients = clients

        self.send_message( message_obj )
        print("Sending message")