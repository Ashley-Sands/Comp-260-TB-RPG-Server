import Sockets.ServerModuleSocket as ServerModuleSocket


class ServerLobbiesSocket( ServerModuleSocket.ServerModuleSocket ):

    def __init__(self, socket, sharded_received_queue=None):

        super().__init__(socket, sharded_received_queue=None)

        self.next_update_time = 0
