# treat as if this is a static class
class MessageTypes:
    # All messages types should have a from client param

    @staticmethod
    def message( from_client, message ):                # m
        """Basic message to all users"""
        return locals()

    @staticmethod
    def client_identity( from_client, nickname ):       # i
        """Request to the client for there identity"""
        return locals()

    @staticmethod
    def client_status( from_client, connected ):        # s
        """Basic message for client connect/dissconnect
        connected is true, otherwise false
        """
        return locals()

