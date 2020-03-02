import json
from messageTypes import *

class Message:

    TYPES = {
        'm': MessageTypes.Message
    }

    def __init__(self, from_client_id, identity_char):

        self.from_client_id = from_client_id
        self.identity = identity_char

        self.to_clients = []    # if this is empty then it needs to be processed by the sever
        self.message = {}

    def set_message( self, json_str ):
        """Set message from json string"""

        self.message = json.loads(json_str)

    def get_message( self ):
        """Gets the message as a json string"""

        return json.dumps( self.message )
