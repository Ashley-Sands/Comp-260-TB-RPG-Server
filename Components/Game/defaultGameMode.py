import Components.Game.baseGameModel as baseGameModel
import Components.Game.serverObject as serverObj
import Common.Protocols.game_types as game_types
import Common.DEBUG as DEBUG

class DefaultGameMode( baseGameModel.BaseGameModel ):

    def __init__(self, socket_handler):
        super().__init__( socket_handler )
        # all the objects that the server tracks excluding the players.
        # dict key = object id, value = server_object
        # TODO: put the objects in the database :)
        self.objects = {
            0: serverObj.ServerObject( 0, game_types.SO_RELIC, (0, 0, 0) ),
            1: serverObj.ServerObject( 1, game_types.SO_RELIC, (0, 0, 0) ),
            2: serverObj.ServerObject( 2, game_types.SO_RELIC, (0, 0, 0) ),
            3: serverObj.ServerObject( 3, game_types.SO_RELIC, (0, 0, 0) )
        }


    def bind_actions_init( self ):

        self.bind_actions = {
            'M': self.move_player,
            '#': self.server_object
        }

    def move_player( self, message_obj ):

        message_obj.to_connections = self.socket_handler.get_connections()
        message_obj.send_message(True)

    def server_object( self, message_obj ):

        # if the object type is of player then we need to update the player
        # otherwise we just have to update self.objects
        if message_obj["type"] == game_types.SO_PLAYER:
            pass
        else:

            obj_id = message_obj["object_id"]
            if obj_id in self.objects:
                self.objects[ obj_id ].set_position( message_obj[ "x" ],
                                                     message_obj[ "y" ],
                                                     message_obj[ "z" ] )
                # send the message to all other clients.
                message_obj.to_connections = self.socket_handler.get_connections()
                message_obj.send_message( True )

            else:   # add it i guess? hmm
                DEBUG.LOGS.print("Object not found! "
                                 "type:", message_obj["type"],
                                 "id:", obj_id,
                                 message_type=DEBUG.LOGS.MSG_TYPE_ERROR)
