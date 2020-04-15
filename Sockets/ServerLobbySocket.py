import Sockets.ServerModuleSocket as ServerModuleSocket


class ServerLobbySocket( ServerModuleSocket.ServerModuleSocket ):

    def __init__(self, socket, sharded_received_queue=None):

        super().__init__(socket, sharded_received_queue=None)

        self.lobby_id = -1
