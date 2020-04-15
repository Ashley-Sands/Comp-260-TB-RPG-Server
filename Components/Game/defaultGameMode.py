import Components.Game.serverObjectComponents as components
import Components.Game.baseGameModel as baseGameModel
import Components.Game.serverObject as serverObj
import Components.Game.helpers as helpers
import Components.Game.analytics as analytics
import Common.Protocols.game_types as game_types
import Common.Protocols.status as status
import Common.message as message
import Common.constants as const
from Common.yield_for_seconds import yield_for_seconds
import Common.taskQueue as taskQueue
import Common.database as database
import Common.DEBUG as DEBUG
import threading
import time

# Win conditions:
# - Last man standing
# - The player has all 4 relics at the start of there turn.

TIME_TO_CLOSE = 15      # the amount of time ofter the game until the game is closed.

class DefaultGameMode( baseGameModel.BaseGameModel ):

    def __init__(self, socket_handler, database, host_id):
        super().__init__( socket_handler, database, host_id )

        self.started = False
        self.ended = False
        self.players_setup = False
        self.completed = False
        self.exit = False
        self.analytics = analytics.Analytics()

        self.scene_name = "default"
        self.min_players, self.max_players = self.database.get_level_info_from_name( self.scene_name )

        self.game_loop_thread = threading.Thread(target=self.update_game)

        # game loop tuple (type time)
        self.game_loop = [ (game_types.GL_CHANGE, 3),
                           (game_types.GL_START, 20),
                           (game_types.GL_END, 3) ]

        self.current_game_loop_id = 0
        self.next_game_state = False
        # needed??
        self.next_game_loop_id = 0
        self.next_player_id = 0
        ###

        self.current_player_id = 0
        self.current_player_connection = None

        # all the objects that the server tracks excluding the players.
        # dict key = object id, value = server_object
        # TODO: put the objects in the database or file :)
        self.relics = {
            0: serverObj.Relic( 0, game_types.SO_RELIC, (0, 1.5, -28.5), active=True ),
            1: serverObj.Relic( 1, game_types.SO_RELIC, (-4, 1.5, -25), active=True ),
            2: serverObj.Relic( 2, game_types.SO_RELIC, (4, 1.5, -25), active=True ),
            3: serverObj.Relic( 3, game_types.SO_RELIC, (0, 1.5, -22), active=True ),
        }

        # TODO: put the objects in the database or file :)
        self.relic_areas = {
            0: serverObj.RelicArea( 0, game_types.SO_RELIC_AREA, (0, 3.5, 5), scale=(19, 6, 19), active=True, bounds=True ),
            1: serverObj.RelicArea( 1, game_types.SO_RELIC_AREA, (0, 3.5, -55), scale=(19, 6, 19), active=True, bounds=True ),
            2: serverObj.RelicArea( 2, game_types.SO_RELIC_AREA, (30, 3.5, -25), scale=(19, 6, 19), active=True, bounds=True ),
            3: serverObj.RelicArea( 3, game_types.SO_RELIC_AREA, (-30, 3.5, -25), scale=(19, 6, 19), active=True, bounds=True )
        }

        self.objects = { **self.relics }

        self.object_id = 3

    def bind_actions_init( self ):

        self.bind_actions = {
            '?': self.client_status,
            'M': self.move_player,
            'A': self.game_action,
            'P': self.collect_object,
            'E': self.explosion,
            'R': self.look_at_position,
            'B': self.request_new_obj_id,
            '#': self.server_object
        }

    def start_game( self ):

        if self.started or self.exit:
            return

        self.current_game_loop_id = -1  # this will be increased to 0 once we enter the update game
        self.current_player_id = -1     # Which will then selected the start player :)
        self.started = True

        self.game_loop_thread.start()

    def update_game( self ):

        while not self.exit and self.started and not self.ended:
            # change current game loop id
            # 0 = Change Player # 1 = Start Turn # 2 = End Turn
            self.current_game_loop_id += 1

            if self.current_game_loop_id >= len(self.game_loop):
                self.current_game_loop_id = 0

            # change player
            if self.current_game_loop_id == 0:
                self.current_player_id = self.get_next_player_id()
                player_connection = self.get_client_by_player_id( self.current_player_id )
                # if the player we change to has all 4 relics they win!
                if player_connection.relic_area.relic_count() == len(self.relics):
                    self.send_win_message( self.current_player_id )
                    self.ended = True

            msg, time_till_next_update = self.get_game_loop_message( self.current_game_loop_id, self.current_player_id )
            msg.send_message()

            for _ in yield_for_seconds( time_till_next_update, self.wake_up_game_loop ):
                pass

            self.next_game_state = False

        DEBUG.LOGS.print( "Game Has Ended. Winner:", self.current_player_id )

        for _ in yield_for_seconds( TIME_TO_CLOSE,
                                    lambda: len( self.socket_handler.get_connections() ) == 0,  # exit func
                                    intervals=0.1 ) :
            pass

        # disconnect all clients
        self.database.clear_game_host(self.host_id)
        connections = self.socket_handler.get_connections()
        for conn in connections:
            conn.safe_close()

        self.completed = True

    def stop_game( self, message ):

        self.exit = True

        self.unbind_all( message )
        print( "" )
        if self.game_loop_thread.is_alive():
            self.game_loop_thread.join()

        self.analytics.stop()

    def wake_up_game_loop( self ):
        return self.exit or self.next_game_state

    def client_status( self, message_obj ):

        if message_obj["status_type"] == status.CS_LEAVE_GAME:
            reg_key = message_obj.from_connection.get_client_key()[1]

            # unset the clients lobby id and disconnect
            self.database.clear_client_lobby( reg_key )

            message_obj.from_connection.safe_close()

    def get_game_loop_message( self, game_loop_id, message_player_id ):

        action, time = self.game_loop[ game_loop_id ]

        msg = message.Message( '>' )
        msg.new_message( const.SERVER_NAME, message_player_id, action, time )
        msg.to_connections = self.socket_handler.get_connections()

        return msg, time

    def get_next_player_id( self ):

        cons = self.socket_handler.get_connections()
        next_min = 999
        min_ = 999
        for c in cons:
            DEBUG.LOGS.print("Current",self.current_player_id ,"PLAYER: ", c.player_id, "next min", next_min, "min", min_)
            if c.health.is_alive():
                if c.player_id < min_:
                    min_ = c.player_id

                if self.current_player_id < c.player_id < next_min:
                    next_min = c.player_id

        if next_min != 999:
            return next_min
        elif min_ != 999:
            return min_
        else:
            return -1 # all deaded??

    def get_object( self, obj_id ):

        if obj_id in self.objects:
            return self.objects[obj_id]
        else:
            return None

    def move_player( self, message_obj ):

        message_obj.to_connections = self.socket_handler.get_connections()
        message_obj.send_message(True)

        self.analytics.add_data( message_obj )

    def collect_object( self, message_obj ):

        # update the clients item
        from_client = message_obj.from_connection
        from_client.current_item = self.get_object( message_obj["object_id"] )

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
            distance = helpers.distance( position, conn.transform.position )
            if distance < const.EXPLOSION_RANGE:
                # send damage message to all clients
                damage_amt = abs(int(const.EXPLOSION_DAMAGE * (1.0-(distance/const.EXPLOSION_RANGE)) ))

                dead = not conn.health.apply_damage( damage_amt )
                health = conn.health.health

                damage.new_message( const.SERVER_NAME, conn.player_id, health, dead )
                damage.send_message()

                DEBUG.LOGS.print( "Damage: ", damage_amt, "health: ", conn.health )

        # work out the other objects some where else :)
        remove_server_object = threading.Thread( target=self.damage_object, args=(self.objects, position) )
        remove_server_object.start()

        self.analytics.add_data( message_obj )

    def damage_object( self, objects, position ):

        for objId in objects:
            # find if any objects are in range.
            distance = helpers.distance( position, objects[objId].transform.position )

            if distance < const.EXPLOSION_RANGE:
                damage_amt = abs( int( const.EXPLOSION_DAMAGE * (1.0 - (distance / const.EXPLOSION_RANGE)) ) )

                # if the object has died remove it and notify the other clients its dead!
                if objects[objId].health is not None and \
                   not objects[objId].health.apply_damage(damage_amt):

                    remove_obj = message.Message('#')
                    remove_obj.new_message( const.SERVER_NAME,
                                            objects[objId].type,
                                            objects[objId].object_id,
                                            *objects[objId].transform.position,  # unpack into x, y, z
                                            game_types.SOA_REMOVE )

                    remove_obj.to_connections = self.socket_handler.get_connections()
                    remove_obj.send_message()

                    del self.objects[ objId ]

    def game_action( self, message_obj ):

        # TODO: we should only be able to launch a projectile if we are not carrying an item.
        actions = [game_types.GA_DROP_ITEM, game_types.GA_LAUNCH_PROJECTILE, game_types.GA_END_TURN]
        action = message_obj["action"]

        if action in actions:
            # update the clients item
            from_client = message_obj.from_connection

            if action == game_types.GA_DROP_ITEM and from_client.current_item is not None:
                from_client.current_item = None

            if action != game_types.GA_END_TURN:
                # send the message to all other clients.
                message_obj.to_connections = self.socket_handler.get_connections()
                message_obj.send_message( True )
            else:
                self.next_game_state = True

        self.analytics.add_data( message_obj )

    def relic_in_area( self, relic ):

        # make sure that it is a relic
        if not isinstance( relic, serverObj.Relic ):
            DEBUG.LOGS.print("Item is not a relic", relic)
            return

        connections = self.socket_handler.get_connections()

        # we only need to check the areas that have an active player.
        for conn in connections:
            area = conn.relic_area
            out_area = None         # the area that the relic has came out of
            if area.bounds.contains( relic.transform ):
                if relic.area == area:
                    DEBUG.LOGS.print( "RELIC No Change!!!!!!!!!!!!!!!!!")
                    return  # no change
                else:
                    DEBUG.LOGS.print( "RELIC Change!!!!!!!!!!!!!!!!!")
                    if relic.area is not None:
                        out_area = relic.area
                        relic.area.remove_relic( relic )

                    area.add_relic( relic )
                    relic.area = area

                    # update the client that gained a relic
                    relic_count = message.Message( '+' )
                    relic_count.new_message( const.SERVER_NAME,
                                             area.object_id,    # for relic_areas the server object id match the player id
                                             area.relic_count() )
                    conn.send_message( relic_count )

                    # update the client who lost a relic
                    if out_area is not None:
                        out_conn = self.get_client_by_player_id( out_area.object_id )

                        if out_conn is None:
                            return

                        relic_count = message.Message( '+' )
                        relic_count.new_message( const.SERVER_NAME,
                                                 out_area.object_id,  # for relic_areas the server object id match the player id
                                                 out_area.relic_count() )
                        out_conn.send_message( relic_count )

                    return

        out_area = None
        if relic.area is not None:
            relic.area.remove_relic( relic )
            out_area = relic.area

        if out_area is not None:
            out_conn = self.get_client_by_player_id( out_area.object_id )

            if out_conn is None:
                return

            relic_count = message.Message( '+' )
            relic_count.new_message( const.SERVER_NAME,
                                     out_area.object_id,  # for relic_areas the server object id match the player id
                                     out_area.relic_count() )
            out_conn.send_message( relic_count )
            return

    def look_at_position( self, message_obj ):

        # send the message to all other clients.
        message_obj.to_connections = self.socket_handler.get_connections()
        message_obj.send_message( True )

    def request_new_obj_id( self, message_obj ):

        message_obj[ "obj_id" ] = self.new_object( message_obj["type"] )
        message_obj.to_connections = [message_obj.from_connection]
        message_obj.send_message()

    def new_object( self, object_type ):

        self.object_id = new_id = self.object_id + 1

        if game_types.SO_BLOCK == object_type:
            health = components.Health(25)
        else:
            health = None

        self.objects[ new_id ] = serverObj.ServerObject( new_id, object_type, (0, 0, 0),
                                                          active=False, health=health )

        return new_id

    def send_win_message( self, win_player_id ):

        win_message = message.Message( 'A' )
        win_message.new_message( const.SERVER_NAME, win_player_id, game_types.GA_END_GAME )
        win_message.to_connections = self.socket_handler.get_connections()
        win_message.send_message()
        DEBUG.LOGS.print( "Win Sent" )

    def server_object( self, message_obj ):

        # if the object type is of player then we need to update the player
        # otherwise we just have to update self.objects
        if message_obj["type"] == game_types.SO_PLAYER:

            client = self.get_client_by_player_id( message_obj["object_id"] )

            if client is not None:
                client.transform.set_position( message_obj[ "x" ],
                                               message_obj[ "y" ],
                                               message_obj[ "z" ] )

                client.transform.set_rotation( message_obj[ "r_x" ],
                                               message_obj[ "r_y" ],
                                               message_obj[ "r_z" ] )

                message_obj.to_connections = self.socket_handler.get_connections()
                message_obj.send_message( True )

        else:
            obj_id = message_obj["object_id"]
            if obj_id in self.objects:

                self.objects[ obj_id ].transform.set_position( message_obj[ "x" ],
                                                     message_obj[ "y" ],
                                                     message_obj[ "z" ] )

                self.objects[ obj_id ].transform.set_rotation ( message_obj[ "r_x" ],
                                                      message_obj[ "r_y" ],
                                                      message_obj[ "r_z" ] )

                # update the relic ares if a relic has been updated :)
                if message_obj["type"] == game_types.SO_RELIC:
                    self.relic_in_area( self.objects[ obj_id ] )

                # once we get some data we can make the object as active and
                # notify other clients to spawn it
                if self.objects[ obj_id ].active is False and message_obj[ "action" ] != game_types.SOA_ADD:
                    DEBUG.LOGS.print("Unable to update object. the object must be active first by setting type to add. ",
                                     message_type=DEBUG.LOGS.MSG_TYPE_WARNING)
                    return
                elif self.objects[ obj_id ].active is False:
                    message_obj[ "action" ] = game_types.SOA_ADD
                    self.objects[ obj_id ].active = True

                # send the message to all other clients.
                message_obj.to_connections = self.socket_handler.get_connections()
                message_obj.send_message( True )

            else:   # add it i guess? hmm
                DEBUG.LOGS.print("Object not found! "
                                 "type:", message_obj["type"],
                                 "id:", obj_id,
                                 message_type=DEBUG.LOGS.MSG_TYPE_ERROR)

        self.analytics.add_data( message_obj )
