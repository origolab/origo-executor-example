class EventListenerStatus:
    """
    The listener status returned by the EventListener. Executor main thread will use this to check the listener status.
    """
    SETUP_FAILED, SETUP_SUCCEEDED= range(2)
    STATUS_EXPLANATION = [
        'listener setup up failed', 'listener setup up succeeded'
    ]
