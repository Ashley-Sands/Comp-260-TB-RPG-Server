
class BaseGameModel:

    def __init__(self):

        self.players_ready_count = 0
        self.bind_actions = {}

    def bind_all( self, message ):
        """binds all functions in bind actions dict to message
        :param message:     the instance of message to bind functions to.
        """
        for ba in self.bind_actions:
            message.bind_action( ba, self.bind_actions[ba] )

    def unbind_all( self, message ):
        """Unbinds all functions in bind actions dict to message
        :param message:     the instance of message to binf functions to.
        """
        for ba in self.bind_actions:
            message.unbind_action( ba, self.bind_actions[ba] )
