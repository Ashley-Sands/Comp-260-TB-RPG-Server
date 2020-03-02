# treat as if this is a static class
class MessageTypes:

    @staticmethod
    def Message( from_client, message ):
        return locals()
