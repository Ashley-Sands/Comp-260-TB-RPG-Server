
class BaseGameModel:

    def __init__(self, socket_handler, database):

        self.socket_handler = socket_handler
        self.database = database
        self.players_ready_count = 0
        self.bind_actions = {}
        self.bind_actions_init()

    def bind_actions_init( self ):
        pass

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

    def get_client_by_player_id( self, player_id ):
        """ Get the serverGameSocket by the player id """

        connections = self.socket_handler.get_connections()

        for conn in connections:
            if conn.player_id == player_id :
                return conn

        return None
