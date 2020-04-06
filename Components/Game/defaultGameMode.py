import Components.Game.baseGameModel as baseGameModel


class DefaultGameMode( baseGameModel.BaseGameModel ):

    def __init__(self, socket_handler):
        super().__init__( socket_handler )

    def bind_actions_init( self ):

        self.bind_actions = {
            'M': self.move_player
        }


    def move_player( self, message_obj ):

        message_obj.to_connections = self.socket_handler.get_connections()
        message_obj.send_message(True)
