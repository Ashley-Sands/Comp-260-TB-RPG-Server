import Components.Game.serverObjectComponents as components
import Common.message as message
import Common.constants as const
import Common.DEBUG as DEBUG

class ServerObject:

    def __init__( self, obj_id, obj_type, pos, rot=(0, 0, 0), scale=(0, 0, 0), active=False, health=None, bounds=None ):
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
        self.bounds = bounds
        self.health = health

    def get_message( self ):

        x, y, z = self.transform.position

        msg = message.Message( '#' )
        msg.new_message( const.SERVER_NAME, self.type, self.object_id, x, y, z )

        return msg
