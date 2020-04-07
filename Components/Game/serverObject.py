import Common.message as message
import Common.constants as const
class ServerObject:

    def __init__( self, obj_id, obj_type, pos ):
        """

        :param obj_type:    The SO type
        :param obj_id:      object id
        :param pos:         position of object : tuple (x, y, z)
        """
        self.type = obj_type              # see Common.Protocols.GameAction for SO types.
        self.object_id = obj_id
        self.position = pos

    def set_position( self, x, y, z ):
        self.position = (x, y, z)

    def get_message( self ):

        x, y, z = self.position

        msg = message.Message( '#' )
        msg.new_message( const.SERVER_NAME, self.type, self.object_id, x, y, z )

        return msg
