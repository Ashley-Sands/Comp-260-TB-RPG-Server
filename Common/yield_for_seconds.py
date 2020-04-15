import time

def yield_for_seconds(t, exit_func=None, intervals=0.000001):
    """

    :param t:           amount of time to yield for. if t < 0 until the exit function is trigger
    :param exit_func:   function for erly exit. if returns true exit erly
    :yields:            True when complete
    """

    end_time = time.time() + t

    while time.time() < end_time or (t < 0 and exit_func is not None):
        yield False
        time.sleep(intervals)    # sleep for 1 nano
        if exit_func is not None and exit_func():
            break

    yield True
