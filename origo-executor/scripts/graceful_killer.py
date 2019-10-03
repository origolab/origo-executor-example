import signal
from datetime import datetime


def format_datetime(dt, _format="%Y-%m-%d %H:%M:%S"):
    return dt.strftime(_format)


def get_current_time(_format="%Y-%m-%d %H:%M:%S"):
    return format_datetime(datetime.now(), _format)


class GracefulKiller(object):
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        print("[%s] Receive Signal: %s" % (get_current_time(), signum))
        self.kill_now = True
