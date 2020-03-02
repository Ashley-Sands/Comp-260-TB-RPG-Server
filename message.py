import json
from messageTypes import *
from messageActions import *


class Message:

    # dict of all new message functions
    # use self.new_message to create the correct type for that message class
    TYPES = {
        'm': MessageTypes.message
    }

    # treat these like singletons , they will become an instance at run time.
    # then we just have to call run and pass in the correct message data :)
    ACTIONS = {
        'm': Action_SendMessage
    }

    init_actions = True

    @staticmethod
    def initialize_actions( send_message_func, get_client_list_func ):
        # create an instance of each actions, ready to run call run when required
        for act in Message.ACTIONS:
            Message.ACTIONS[ act ] = Message.ACTIONS[ act ]( send_message_func, get_client_list_func )

        Message.init_actions = False


    def __init__(self, from_client_id, identity_char):

        if Message.init_actions:
            Message.initialize_actions()

        self.identity = identity_char
        self.from_client_id = from_client_id
        self.to_clients = []    # if this is empty then it needs to be processed by the sever
        self.message = {}

        # function to get a new message dict for self.identity
        self.new_message = Message.TYPES[identity_char]


    def set_message( self, json_str ):
        """Set message from json string"""

        self.message = json.loads(json_str)

    def get_message( self ):
        """Gets the message as a json string"""

        return json.dumps( self.message )
