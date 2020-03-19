import queue as q
import threading
import datetime
import time
import os.path

# treat as if static :)
class DEBUG:

    MESSAGE_TYPE_DEFAULT = 1
    MESSAGE_TYPE_WARNING = 2
    MESSAGE_TYPE_ERROR   = 3


    debug_mode = True
    inited = False
    active = False
    print_que = None    # Queue of tuples (type, message)
    debug_thread = None
    print_debug_intervals = 1

    __log_path = "logs/"
    __log_name = "log.txt"

    __log_messages_to_file = False
    __log_warning_to_file = False
    __log_errors_to_file = True


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
    def print( *argv, message_type=1, sept=' ' ):

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

        DEBUG.print_que.put( (message_type, "{0} | {1} | {2}".format(time_str, message_type_name, sept.join(argv))) )

    @staticmethod
    def debug_print_thread( ):

        if not DEBUG.inited or not DEBUG.debug_mode:
            return

        print("started debug thread")

        DEBUG.active = True

        while DEBUG.active:
            while not DEBUG.print_que.empty():
                msg_type, message = DEBUG.print_que.get(block=True, timeout=None)
                print( message )
                DEBUG.add_to_logs(msg_type, message)

            time.sleep(DEBUG.print_debug_intervals)   # theres no need to

        DEBUG.active = False
        print("dead debug thread")

    @staticmethod
    def set_log_to_file( message=False, warning=False, error=True ):
        DEBUG.__log_messages_to_file = message
        DEBUG.__log_warning_to_file = warning
        DEBUG.__log_error_to_file = error

    @staticmethod
    def add_to_logs( msg_type, message ):

        update_log = msg_type == DEBUG.MESSAGE_TYPE_DEFAULT and DEBUG.__log_messages_to_file or \
                     msg_type == DEBUG.MESSAGE_TYPE_WARNING and DEBUG.__log_warning_to_file or \
                     msg_type == DEBUG.MESSAGE_TYPE_ERROR and DEBUG.__log_errors_to_file

        if update_log:
            if os.path.exists(DEBUG.__log_path + DEBUG.__log_name):
                file_mode = 'a'
            else:
                file_mode = 'w'

            print(file_mode)

            with open(DEBUG.__log_path + DEBUG.__log_name, file_mode) as log:
                log.write( "\n"+message )