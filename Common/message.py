import json
import Common.DEBUG as DEBUG
from Common.Protocols import request_types, info_types, scene_control, status, common, test, game_types


class Message:

    # a list of all message types, there not all necessarily used in all modules but
    # for a easier life and reference
    TYPES = {
        '!': status.server_status,
        '?': status.client_status,
        '&': test.ping,
        'i': request_types.identity_request,
        'I': request_types.identity_status,
        'l': info_types.lobby_list,
        'L': request_types.join_lobby_request,
        's': scene_control.scene_request,
        'C': info_types.lobby_client_list,
        'O': info_types.lobby_info,
        'm': common.message,
        'G': info_types.game_client_list,

        'M': game_types.move_player,
        'A': game_types.game_Action,
        'P': game_types.collect_item,
        'E': game_types.explosion,
        'D': game_types.apply_damage,
        'R': game_types.look_at,
        '#': game_types.server_object
    }

    # Action functions need to be bound onto there TYPE 'char'
    # Use (static) bind_action and unbind_action functions, to do such task
    # callback functions require a param of type (Common.)Message
    ACTION = { }    # dict. Key: identity char. value list of functions [func0, func2, ...] ( dict[char][int] )

    def __init__( self, identity_char, from_connection=None ):
        """

        :param identity_char:       # the identity of the message (or TYPE char)
        :param from_connection:     # the connection that we received the message from (if applicable)
        """

        self.ERR = False

        if identity_char not in Message.TYPES :
            DEBUG.LOGS.print("Error: Message type", identity_char, "not found")
            self.ERR = True
            return

        self.identity = identity_char
        self.from_connection = from_connection     # this is only set when recived
        self.to_connections = []
        self.message = {}

        # the function to create a new message
        self.__new_message = Message.TYPES[identity_char]

    def __getitem__(self, item):
        """Shortcut to access message dict"""
        return self.message[item]

    def __setitem__(self, item, value):
        """Shortcut to set message dict"""
        self.message[item] = value

    @staticmethod
    def bind_action(identity_char, func):
        """Add the func to the actions table"""
        if identity_char not in Message.ACTION:
            Message.ACTION[identity_char] = [func]
        else:
            Message.ACTION[identity_char].append(func)

    @staticmethod
    def unbind_action( identity_char, func ):
        """Remove the func from the actions list"""
        if identity_char in Message.ACTION:
            Message.ACTION[identity_char].remove(func)
            # remove the identity if there are no functions left bound to the event.
            if len(Message.ACTION[identity_char]) == 0:
                del Message.ACTION[identity_char]


    def run_action( self ):
        """Run all the actions bound to this messages identity"""

        if not self.ERR and self.identity in Message.ACTION:
            for func in Message.ACTION[self.identity]:
                func( self )

    def new_message( self, *params ):
        """
            Sets a new message
            See Message identity char TYPE of params!
        """

        if not self.ERR:
            self.message = Message.TYPES[self.identity](*params)

    def send_message( self, ignore_from_client=False ):

        for c in self.to_connections:

            if ignore_from_client and self.from_connection == c:
                continue

            c.send_message( self )

    def set_from_json( self, from_name, json_str ):
        """set self.message with json string"""
        try:
            self.message = json.loads(json_str)
        except Exception as e:
            DEBUG.LOGS.print("Could not convert from json: ", json_str, message_type=DEBUG.LOGS.MSG_TYPE_ERROR)

        self.message["from_client_name"] = from_name

    def get_json( self ):
        """get self.message as a json string"""
        try:
            return json.dumps( self.message )
        except Exception as e:
            DEBUG.LOGS.print("Could not convert to json: (-E001)", message_type=DEBUG.LOGS.MSG_TYPE_ERROR)
            return "-E001"
