import DEBUG
import json
from messageTypes import *
from messageActions import *
from playerMessageTypes import *
from playerMessageActions import *

class Message:

    # dict of all new message functions
    # use self.new_message to create the correct type for that message class
    TYPES = {
        # General
        'm': MessageTypes.message,
        'i': MessageTypes.client_identity,
        's': MessageTypes.status,
        'g': MessageTypes.game_request,
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
        'm': Action_SendMessage,
        'i': Action_ClientIdentity,
        's': Action_status,
        'g': Action_GamesRequest,
        'j': Action_JoinLobbyRequest,

        # in game
        'J': Action_JoinedGame,
        'S': Action_StartGame,
        'M': PlayerAction_Move
    }

    init_actions = True

    @staticmethod
    def initialize_actions( game_inst, send_message_func, get_client_list_func, get_client_func, get_games_func ):
        # create an instance of each actions, ready to run call run when required
        for act in Message.ACTIONS:
            Message.ACTIONS[ act ] = Message.ACTIONS[ act ]( game_inst,
                                                             send_message_func,
                                                             get_client_list_func,
                                                             get_client_func,
                                                             get_games_func)

        Message.init_actions = False

    def __init__(self, from_client_key, identity_char):

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

    def run_action( self ):

        if self.identity not in Message.ACTIONS:
            DEBUG.DEBUG.print("identity", self.identity, "has no action")
            return

        Message.ACTIONS[ self.identity ].run( self )

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

        return json.dumps( self.message )
