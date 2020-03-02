
class MessageAction:

    def __init__( self, send_message_func, get_client_list_func ):
        self.send_message = send_message_func
        self.get_clients = get_client_list_func

    def action( self, message_obj ):
        pass

class Action_SendMessage( MessageAction ):

    def run( self, message_obj ):

        clients = self.get_clients( message_obj.from_client_id )
        message_obj.to_clients = clients

        self.send_message( message_obj )