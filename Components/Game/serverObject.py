import Components.Game.serverObjectComponents as components
import Common.message as message
import Common.constants as const
import Common.DEBUG as DEBUG

class ServerObject:

    def __init__( self, obj_id, obj_type, pos, rot=(0, 0, 0), scale=(1, 1, 1), active=False, health=None, bounds=False ):
        """

        :param obj_type:    The SO type
        :param obj_id:      object id
        :param pos:         position of object : tuple (x, y, z)
        :param rot:         rotation of object : tuple (x, y, z)
        :param active:      is the object in uses.
        :param health:      the amount of health the object should have. <0 == invincible object.
        """
        self.active = active
        self.type = obj_type              # see Common.Protocols.GameAction for SO types.
        self.object_id = obj_id

        self.transform = components.Transform(pos, rot, scale)
        self.bounds = None
        self.health = health

        if bounds:
            self.bounds = components.Bounds( self.transform )

    def get_message( self ):

        x, y, z = self.transform.position

        msg = message.Message( '#' )
        msg.new_message( const.SERVER_NAME, self.type, self.object_id, x, y, z )

        return msg


class Relic( ServerObject ):

    def __init__(self, obj_id, obj_type, pos, rot=(0, 0, 0), scale=(1, 1, 1), active=False, health=None, bounds=False):

        super().__init__( obj_id, obj_type, pos, rot=rot, scale=scale, active=active, health=health, bounds=bounds )

        self.area = None


class RelicArea( ServerObject ):

    def __init__( self, obj_id, obj_type, pos, rot=(0, 0, 0), scale=(1, 1, 1), active=False, health=None, bounds=False ):
        super().__init__( obj_id, obj_type, pos, rot=rot, scale=scale, active=active, health=health, bounds=bounds )
        self.relics = []

    def add_relic( self, relic ):
        self.relics.append( relic )

    def remove_relic( self, relic ):
        if relic in self.relics:
            self.relics.remove(relic)

    def relic_count( self ):
        return len(self.relics)
