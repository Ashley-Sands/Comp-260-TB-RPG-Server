# treat as if this is a static class
class MessageTypes:

    @staticmethod
    def message( from_client, message ):
        return locals()
