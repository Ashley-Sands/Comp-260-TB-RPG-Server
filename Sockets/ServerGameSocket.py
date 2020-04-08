import Sockets.ServerModuleSocket as ServerModuleSocket


class ServerGameSocket( ServerModuleSocket.ServerModuleSocket ):

    def __init__(self, socket):

        super().__init__(socket)

        # Game stats
        self.ready = False
        self.player_id = -1     # < 0 unset.

        # Game
        self.position = (0, 0, 0)
        self.current_item = None

    def get_player_info( self ):
        """ gets the players info.

        :return:    tuple ( client_id, nickname, player_id)
        """

        self.thread_lock.acquire()
        info = (self._client_db_id, self.client_nickname, self.player_id)
        self.thread_lock.release()

        return info

    def set_position( self, x, y, z ):

        self.position = (x, y, z)
