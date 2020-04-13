import Sockets.ServerModuleSocket as ServerModuleSocket
import Components.Game.serverObjectComponents as components

class ServerGameSocket( ServerModuleSocket.ServerModuleSocket ):

    def __init__(self, socket):

        super().__init__(socket)

        # Game stats
        self.ready = False
        self.set = False    # ready set go!

        self.player_id = -1     # < 0 unset.

        # Game
        self.transform = components.Transform( (0, 0, 0), (0, 0, 0), (1, 1, 1) )
        self.health = components.Health(100)
        self.ammo = 25
        self.blocks = 10

        self.current_item = None
        self.relic_area = None


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

    def set_rotation( self, x, y, z ):
        self.rotation = ( x, y, z )
