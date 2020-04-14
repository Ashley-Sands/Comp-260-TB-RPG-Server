import signal

class SignalHandler:

    def __init__( self ):

        self.triggered = False
        signal.signal(signal.SIGTERM, self.handle_signal)

    def handle_signal( self, signum, frame ):
        self.triggered = True
        print("Helloo")