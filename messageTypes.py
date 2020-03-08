# treat as if this is a static class
class MessageTypes:
    # All messages types should have a from client param

    @staticmethod
    def message( from_client, message ):
        """Basic message to all users"""
        return locals()

    @staticmethod
    def client_status( from_client, connected ):
        """Basic message for client connect/dissconnect
        connected is true, otherwise false
        """
        return locals()
