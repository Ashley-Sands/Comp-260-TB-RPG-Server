import queue as q
import threading
import datetime
import time
import os.path


# treat as if static :)
class LOGS:

    MSG_TYPE_DEFAULT = 1
    MSG_TYPE_WARNING = 2
    MSG_TYPE_ERROR   = 3
    MSG_TYPE_FATAL   = 4
    MSG_TYPE_TIMES   = 5

    debug_mode = True
    debug_sql = False
    print_times_only = True
    que_pre_init_msg = True
    inited = False
    active = False
    print_que = q.Queue()    # Queue of tuples (type, message)
    debug_thread = None
    print_debug_intervals = 0 #1

    __log_path = "logs/"
    __log_name = "log.txt"

    __log_messages_to_file = False
    __log_warning_to_file = False
    __log_errors_to_file = True
    __log_fatal_to_file = True


    @staticmethod
    def init():
        """This must be called to start the debug thread
        The thread wll not start unless debug_mode is set to True
        """
        if LOGS.inited or not LOGS.debug_mode:
            return

        LOGS.debug_thread = threading.Thread(target=LOGS.debug_print_thread)

        LOGS.inited = True
        LOGS.print("DEBUG Inited Successfully")
        LOGS.debug_thread.start()

    @staticmethod
    def print( *argv, message_type=1, sept=' ' ):

        if not LOGS.debug_mode or (not LOGS.que_pre_init_msg and not LOGS.inited):
            return

        if LOGS.print_times_only and message_type != LOGS.MSG_TYPE_TIMES:
            return

        now = datetime.datetime.utcnow()
        time_str = now.strftime("%m/%d/%Y @ %H:%M:%S.%f")

        # make sure all the values in argv are strings
        argv = [ str( a ) for a in argv ]


        if message_type == LOGS.MSG_TYPE_WARNING:
            message_type_name = "WARNING"
        elif message_type == LOGS.MSG_TYPE_ERROR:
            message_type_name = "ERROR  "
        elif message_type == LOGS.MSG_TYPE_FATAL:
            message_type_name = "FATAL"
        else:
            message_type_name = "MESSAGE"

        LOGS.print_que.put( (message_type, "{0} | {1} | {2}".format(time_str, message_type_name, sept.join(argv))) )

    @staticmethod
    def debug_print_thread( ):

        if not LOGS.inited or not LOGS.debug_mode:
            return

        print("started debug thread")

        LOGS.active = True

        while LOGS.active:

            msg_type, message = LOGS.print_que.get(block=True, timeout=None)

            print( LOGS.__get_console_color(message, msg_type) )
            LOGS.add_to_logs(msg_type, message)

            time.sleep(LOGS.print_debug_intervals)   # theres no need to

        LOGS.active = False
        print("dead debug thread")

    @staticmethod
    def __get_console_color( msg, msg_type ):

        msg = msg.split( "|" )

        cols = {
            LOGS.MSG_TYPE_DEFAULT: "\033[1;32m",
            LOGS.MSG_TYPE_WARNING: "\033[1;33m",
            LOGS.MSG_TYPE_ERROR: "\033[1;31m",
            LOGS.MSG_TYPE_FATAL: "\033[1;31;40m",
            LOGS.MSG_TYPE_TIMES: "\033[1;35m",
        }

        return msg[ 0 ] + "|"+ cols[msg_type] + msg[ 1 ] + "\033[0;37m|" + '|'.join( msg[ 2: ] )

    @staticmethod
    def set_log_to_file( message=False, warning=False, error=True, fatal=True ):
        LOGS.__log_messages_to_file = message
        LOGS.__log_warning_to_file = warning
        LOGS.__log_error_to_file = error
        LOGS.__log_fatal_to_file = fatal

    @staticmethod
    def add_to_logs( msg_type, message ):

        update_log = msg_type == LOGS.MSG_TYPE_DEFAULT and LOGS.__log_messages_to_file or \
                     msg_type == LOGS.MSG_TYPE_WARNING and LOGS.__log_warning_to_file or \
                     msg_type == LOGS.MSG_TYPE_ERROR and LOGS.__log_errors_to_file or \
                     msg_type == LOGS.MSG_TYPE_FATAL and LOGS.__log_fatal_to_file

        if update_log:
            if os.path.exists(LOGS.__log_path + LOGS.__log_name):
                file_mode = 'a'
            else:
                file_mode = 'w'

            with open(LOGS.__log_path + LOGS.__log_name, file_mode) as log:
                log.write( "\n"+message )

    @staticmethod
    def close():

        LOGS.active = False

        # we must put an message into the que to make sure it gets un blocked
        LOGS.print( "Closing Debug (Unblock message)" )