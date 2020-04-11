import Common.message as message
import Common.constants as const
import Common.DEBUG as DEBUG

class ServerObject:

    def __init__( self, obj_id, obj_type, pos, rot=(0, 0, 0), active=False, health=-1 ):
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

        self.position = pos
        self.rotation = rot

        self.has_health = health > 0
        self.health = health

    def set_position( self, x, y, z ):
        self.position = (x, y, z)

    def set_rotation( self, x, y, z ):
        self.rotation = (x, y, z)

    def get_message( self ):

        x, y, z = self.position

        msg = message.Message( '#' )
        msg.new_message( const.SERVER_NAME, self.type, self.object_id, x, y, z )

        return msg

    def apply_damage( self, damage ):
        """ Applies damage to the object if it has health
            :returns True if still alive
        """

        if self.has_health:
            self.health -= damage

            DEBUG.LOGS.print( "Ouch! obj id,", self.object_id,
                              "type ", self.type,
                              "has taken ", damage, "damage",
                              "new health", self.health )

        return not self.has_health or self.health > 0
