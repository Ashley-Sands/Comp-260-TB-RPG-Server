import message

# these are actions that are not trigger by send/receiving messages


class StaticActions:

    @staticmethod
    def send_client_status( status, client_key, client_name, get_client_list_func, send_message_func ):

        new_client_message = message.Message( client_key, 's' )
        new_message = new_client_message.new_message( client_name, status )
        new_client_message.message = new_message
        new_client_message.to_clients = get_client_list_func( [ client_key ] )

        send_message_func( new_client_message )