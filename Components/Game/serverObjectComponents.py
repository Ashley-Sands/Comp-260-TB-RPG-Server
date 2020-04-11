
class Transform:

    def __init__( self, position, rotation, scale ):
        """

        :param position:    tuple (x, y, z)
        :param rotation:    tuple (x, y, z)
        :param scale:       tuple (x, y, z)
        """
        self.position = position
        self.rotation = rotation
        self.scale = scale
        self.half_scale = (scale[ 0 ] / 2.0, scale[ 1 ] / 2.0, scale[ 2 ] / 2.0)


class Health:

    def __init__( self, health ):

        self.health = health


class Bounds:

    def __init__( self, transform ):

        self.transform = transform

    def __min_bounds( self ):

        return ( self.transform.position[0] - self.transform.half_scale[0],
                 self.transform.position[1] - self.transform.half_scale[1],
                 self.transform.position[2] - self.transform.half_scale[2] )

    def __max_bounds( self ):

        return (self.transform.position[ 0 ] + self.transform.half_scale[ 0 ],
                self.transform.position[ 1 ] + self.transform.half_scale[ 1 ],
                self.transform.position[ 2 ] + self.transform.half_scale[ 2 ])

    def contains( self, transform ):
        """returns true if the position of the transform is in the bounds"""

        x, y, z = transform.position
        min_x, min_y, min_z = self.__min_bounds()
        max_x, max_y, max_z = self.__max_bounds()

        return min_x < x < max_x and min_y < y < max_y and min_z < z < max_z
