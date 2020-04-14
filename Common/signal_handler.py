import signal

class SignalHandler:

    def __init__( self, test=False ):

        self.testing = test
        self.triggered = False

        if test:
            signal.signal( signal.SIGALRM, self.handle_signal )  # test alarm signal call test(t=2) to trigger in 2 seconds
        else:
            signal.signal(signal.SIGTERM, self.handle_signal)    # handle the system terminate single

    def test( self, t=2 ):

        if self.testing:
            signal.alarm(t)

    def handle_signal( self, signum, frame ):
        self.triggered = True
        print("Helloo")