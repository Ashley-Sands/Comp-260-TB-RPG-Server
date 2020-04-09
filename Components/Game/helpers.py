import math
import Common.DEBUG as DEBUG

def distance( pos_a, pos_b ):
    """

    :param position_a:      tuple(x, y, z)
    :param position_b:      tuple(x, y, z)
    :return:                float distance
    """
    distance = math.sqrt( math.pow(pos_b[0] - pos_a[0], 2) +
                      math.pow(pos_b[1] - pos_a[1], 2) +
                      math.pow(pos_b[2] - pos_a[2], 2) )

    DEBUG.LOGS.print( "Distance:", distance )

    return distance
