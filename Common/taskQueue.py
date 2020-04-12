import threading
import time
import Common.DEBUG as DEBUG

class Task:

    def __init__( self,):
        self.task_id = -1
        self.stop_ = False
        self.tasks = {}

    def new_task( self, message_obj, delay, complete_func ):
        """ starts a new task

        :param message_obj:     message that to sent
        :param delay:           delay until the message is send
        :param complete_func:   callback function when task in complete must has int param for task id
        :return:                new task id
        """
        if self.stop_:
            return -1

        self.task_id += 1
        self.tasks[ self.task_id ] = threading.Thread( target=self.task,
                                                       args=(self.task_id, message_obj, delay, complete_func) )
        self.tasks[ self.task_id ].start()

        self.clean()

        return self.task_id

    def stop( self ):
        self.stop_ = True

        for t in self.tasks:
            if self.tasks[t].is_alive():
                self.tasks[t].join()

        DEBUG.LOGS.print( "TASKS STOPED" )

    def clean( self ):

        for t in list(self.tasks):
            if not self.tasks[t].is_alive():
                del self.tasks[t]

    def task( self, task_id, message_obj, delay, complete_func):

        time.sleep( delay )

        if self.stop_:
            return

        message_obj.send_message()
        complete_func(task_id)
