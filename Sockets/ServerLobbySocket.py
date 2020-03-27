import Sockets.ServerModuleSocket as ServerModuleSocket


class ServerLobbySocket( ServerModuleSocket.ServerModuleSocket ):

    def __init__(self, socket):

        super().__init__(socket)

        self.lobby_id = -1
