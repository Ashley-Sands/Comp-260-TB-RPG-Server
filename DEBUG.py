import queue as q
import threading
import datetime
import time

# treat as if static :)
class DEBUG:

    MESSAGE_TYPE_DEFAULT = 1
    MESSAGE_TYPE_WARNING = 2
    MESSAGE_TYPE_ERROR   = 3


    debug_mode = True
    inited = False
    active = False
    print_que = None
    debug_thread = None
    print_debug_intervals = 1


    @staticmethod
    def init():
        """This must be called to start the debug thread
        The thread wll not start unless debug_mode is set to True
        """
        if DEBUG.inited or not DEBUG.debug_mode:
            return

        DEBUG.print_que = q.Queue()

        DEBUG.debug_thread = threading.Thread(target=DEBUG.debug_print_thread)

        DEBUG.inited = True
        DEBUG.print("DEBUG Inited Successfully")
        DEBUG.debug_thread.start()

    @staticmethod
    def print( *argv, message_type=0, sept=' ' ):

        if not DEBUG.debug_mode or not DEBUG.inited:
            return

        now = datetime.datetime.utcnow()
        time_str = now.strftime("%m/%d/%Y @ %H:%M:%S.%f")

        # make sure all the values in argv are strings
        argv = [ str( a ) for a in argv ]


        if message_type == DEBUG.MESSAGE_TYPE_WARNING:
            message_type_name = "WARNING"
        elif message_type == DEBUG.MESSAGE_TYPE_ERROR:
            message_type_name = "ERROR  "
        else:
            message_type_name = "MESSAGE"

        DEBUG.print_que.put( "{0} | {1} | {2}".format(time_str, message_type_name, sept.join(argv)) )

    @staticmethod
    def debug_print_thread( ):

        if not DEBUG.inited or not DEBUG.debug_mode:
            return

        print("started debug thread")

        DEBUG.active = True

        while DEBUG.active:
            while not DEBUG.print_que.empty():
                print( DEBUG.print_que.get(block=True, timeout=None) )

            time.sleep(DEBUG.print_debug_intervals)   # theres no need to

        DEBUG.active = False
        print("dead debug thread")
