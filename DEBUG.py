import queue as q
import threading
import datetime
import time

# treat as if static :)
class DEBUG:

    debug_mode = True
    inited = False
    active = False
    print_que = None
    debug_thread = None

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
    def print( *argv, error=False, sept=' ' ):

        if not DEBUG.debug_mode or not DEBUG.inited:
            return

        now = datetime.datetime.now()
        time_str = now.strftime("%m/%d/%Y @ %H:%M:%S.%f")

        # make sure all the values in argv are strings
        argv = [ str( a ) for a in argv ]

        message_type = "MESSAGE"

        if error:
            message_type = "ERROR  "

        DEBUG.print_que.put( "{0} | {1} | {2}".format(time_str, message_type, sept.join(argv)) )

    @staticmethod
    def debug_print_thread( ):

        if not DEBUG.inited or not DEBUG.debug_mode:
            return

        print("started debug thread")

        DEBUG.active = True

        while DEBUG.active:
            while not DEBUG.print_que.empty():
                print( DEBUG.print_que.get(block=True, timeout=None) )

            time.sleep(0.5)

        DEBUG.active = False
        print("dead debug thread")
