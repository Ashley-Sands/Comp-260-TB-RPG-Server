import Sockets.ServerModuleSocket as ServerModuleSocket


class ServerGameSocket( ServerModuleSocket.ServerModuleSocket ):

    def __init__(self, socket):

        super().__init__(socket)

        # Game stats
        self.ready = False

