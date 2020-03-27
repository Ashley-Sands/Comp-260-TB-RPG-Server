import Common.DEBUG as DEBUG
import time

def processes_ping( message_obj ):

    DEBUG.DEBUG.print( "Processing ping" )

    now_millis = time.time_ns() / 1000000
    message_obj[ "server_receive_time" ] = now_millis

    message_obj.from_connection.send_message( message_obj )
