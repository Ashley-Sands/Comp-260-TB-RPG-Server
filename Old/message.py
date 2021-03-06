import DEBUG
import traceback, sys
import json
from messageTypes import *
from messageActions import *
from playerMessageTypes import *
from playerMessageActions import *

class Message_OLD:

    # dict of all new message functions
    # use self.new_message to create the correct type for that message class
    TYPES = {
        # General
        'm': MessageTypes.message,
        'i': MessageTypes.client_identity,
        'r': MessageTypes.client_registered,
        # ----------
        's': MessageTypes.status,
        'g': MessageTypes.current_lobby_request,
        'j': MessageTypes.join_lobby_request,
        'd': MessageTypes.game_info,  # TODO: add action. if the client sends this to use we need to fill in the missing data and return it

        'b': MessageTypes.launch_game,
        'l': MessageTypes.leave_game_request,
        # Joining game
        'J': MessageTypes.joined_game,
        'P': MessageTypes.pre_start_game,
        'S': MessageTypes.start_game,
        # in game
        'C': PlayerMessageTypes.change_player,
        'M': PlayerMessageTypes.move_player

    }

    # treat these like singletons , they will become an instance at run time.
    # then we just have to call run and pass in the correct message data :)
    # Not all message types have actions :) ie.
    ACTIONS = {
        'm': Action_SendMessage,                    # needs updateing
        'i': Action_ClientIdentity,                 # up
        's': Action_status,
        'g': Action_GamesRequest,                   # needs updateing.
        'j': Action_JoinLobbyRequest,               # wip

        # in game
        'J': Action_JoinedGame,
        'S': Action_StartGame,
        'M': PlayerAction_Move
    }

    # dict of lists Key: identity value list of functions (with a from_client_key (type socket) param)
    # the key does not have to be in the action list but it must be a valid identity
    action_callbacks = {}

    init_actions = True

    @staticmethod
    def initialize_actions( database, send_message_func, get_client_list_func, get_client_func, available_actions=[], game_inst=None ):
        '''

        :param database:             the database to get client list ect from
        :param send_message_func:    function to use for sending message
        :param get_client_list_func  function to get list of players client id's
        :param get_client_func       function to get a client by its client id
        :param available_actions:    a list of action chars, if empty list uses all actions
        :param game_inst:            the game instance (default is None)
        :return:
        '''
        # create an instance of each actions, ready to run call run when required
        # remove any actions that are not available
        for act in Message.ACTIONS:
            if len(available_actions) > 0 and act not in available_actions:
                del Message.ACTIONS[act]
            else:
                Message.ACTIONS[ act ] = Message.ACTIONS[ act ]( database,
                                                                 send_message_func,
                                                                 get_client_list_func,
                                                                 get_client_func,
                                                                 game_inst
                                                                 )

        Message.init_actions = False

    def __init__(self, from_client_key, identity_char):

        if identity_char not in Message.TYPES:
            DEBUG.DEBUG.print("Type Not Found. Type:", identity_char, message_type=DEBUG.DEBUG.MESSAGE_TYPE_ERROR)
            return

        if Message.init_actions:
            Message.initialize_actions()

        if identity_char not in Message.TYPES :
            DEBUG.DEBUG.print("Error: Message type", identity_char, "not found")

        self.identity = identity_char
        self.from_client_key = from_client_key
        self.to_clients = []    # if this is empty then it needs to be processed by the sever
        self.message = {}

        # functions to get a new message dict for self.identity
        self.new_message = Message.TYPES[identity_char]


    """Shortcut to access message dict"""
    def __getitem__(self, item):
        return self.message[item]

    @staticmethod
    def action_bind( identity, func ):

        if identity not in Message.TYPES:   # bad identity
            DEBUG.DEBUG.print("Unable to bind function to identity:", identity, "identity is invalid", message_type=DEBUG.DEBUG.MESSAGE_TYPE_ERROR)
            return

        if identity not in Message.action_callbacks:
            Message.action_callbacks[identity] = [func]
        else:
            Message.action_callbacks[identity].append( func )
    @staticmethod
    def action_unbind( identity, func ):

        if identity in Message.action_callbacks and func in Message.action_callbacks[identity]:
            Message.action_callbacks[ identity ].remove( func )

    def run_action( self ):
        """Runs the action followed by the callback. if there no actions just the callbacks are triggered"""
        if self.identity in Message.ACTIONS:
            Message.ACTIONS[ self.identity ].run( self )
        else:
            DEBUG.DEBUG.print("identity", self.identity, "has no action")

        # trigger the callbacks
        if self.identity in Message.action_callbacks:
            for cb in Message.action_callbacks[self.identity]:
                cb(self.from_client_key)

    def set_message( self, from_client_name, json_str ):
        """Set message from json string"""
        try:
            self.message = json.loads(json_str)
        except Exception as e:
            DEBUG.DEBUG.print (e)
            DEBUG.DEBUG.print (json_str)
        # We should assume that the client has not set who it is from.
        # It is required by the client when receiving messages tho.
        self.message["from_client"] = from_client_name


    def get_message( self ):
        """Gets the message as a json string"""

        try:
            return json.dumps( self.message )
        except Exception as e:
            DEBUG.DEBUG.print( e, "\n", self.message, "\nid:", self.identity,
                               message_type=DEBUG.DEBUG.MESSAGE_TYPE_ERROR )
            return ""

