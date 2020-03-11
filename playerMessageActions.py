import messageActions


class PlayerAction_Move( messageActions.MessageAction ):

    def run( self, message_obj ):

        from_client = self.get_client( message_obj.from_client_key )

        if from_client == None:
            print("Error can not find game / client")
            return

        game = from_client.get_active_game()
        clients = self.get_client_list( [from_client.key], game )

        message_obj.to_clients = clients
        self.send_message( message_obj )
