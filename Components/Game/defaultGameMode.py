import Components.Game.baseGameModel as baseGameModel
import Components.Game.serverObject as serverObj
import Components.Game.helpers as helpers
import Common.Protocols.game_types as game_types
import Common.message as message
import Common.constants as const
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
            'A': self.game_action,
            'P': self.collect_object,
            'E': self.explosion,
            'R': self.look_at_position,
            '#': self.server_object
        }

    def move_player( self, message_obj ):

        message_obj.to_connections = self.socket_handler.get_connections()
        message_obj.send_message(True)

    def collect_object( self, message_obj ):

        # update the clients item
        from_client = message_obj.from_connection
        from_client.urrent_item = message_obj["object_id"]

        # send the message to all other clients.
        message_obj.to_connections = self.socket_handler.get_connections()
        message_obj.send_message(True)

    def explosion( self, message_obj ):

        position = ( message_obj["x"],
                     message_obj["y"],
                     message_obj["z"] )

        connections = self.socket_handler.get_connections()

        damage = message.Message( 'D' )
        damage.to_connections = connections

        for conn in connections:
            distance = helpers.distance( position, conn.position )
            if distance < const.EXPLOSION_RANGE:
                # send damage message to all clients
                damage_amt = abs(int(const.EXPLOSION_DAMAGE * (1.0-(distance/const.EXPLOSION_RANGE)) ))

                conn.health -= damage_amt

                damage.new_message( const.SERVER_NAME, conn.player_id, damage_amt, conn.health <= 0 )
                damage.send_message()

                DEBUG.LOGS.print( "Damage: ", damage_amt, "health: ", conn.health )

    def game_action( self, message_obj ):

        actions = [game_types.GA_DROP_ITEM, game_types.GA_LAUNCH_PROJECTILE]

        if message_obj["action"] in actions:
            # update the clients item
            from_client = message_obj.from_connection
            from_client.current_item = None

            # send the message to all other clients.
            message_obj.to_connections = self.socket_handler.get_connections()
            message_obj.send_message( True )

    def look_at_position( self, message_obj ):

        DEBUG.LOGS.print("Hreloooo look at position")
        # send the message to all other clients.
        message_obj.to_connections = self.socket_handler.get_connections()
        message_obj.send_message( True )


    def server_object( self, message_obj ):

        # if the object type is of player then we need to update the player
        # otherwise we just have to update self.objects
        if message_obj["type"] == game_types.SO_PLAYER:

            client = self.get_client_by_player_id( message_obj["object_id"] )

            if client is not None:
                client.set_position( message_obj[ "x" ],
                                     message_obj[ "y" ],
                                     message_obj[ "z" ] )

                client.set_rotation( message_obj[ "r_x" ],
                                     message_obj[ "r_y" ],
                                     message_obj[ "r_z" ] )
        else:
            obj_id = message_obj["object_id"]
            if obj_id in self.objects:
                self.objects[ obj_id ].set_position( message_obj[ "x" ],
                                                     message_obj[ "y" ],
                                                     message_obj[ "z" ] )

                self.objects[ obj_id ].set_rotation ( message_obj[ "r_x" ],
                                                      message_obj[ "r_y" ],
                                                      message_obj[ "r_z" ] )

                # send the message to all other clients.
                message_obj.to_connections = self.socket_handler.get_connections()
                message_obj.send_message( True )

            else:   # add it i guess? hmm
                DEBUG.LOGS.print("Object not found! "
                                 "type:", message_obj["type"],
                                 "id:", obj_id,
                                 message_type=DEBUG.LOGS.MSG_TYPE_ERROR)
