import logging
import socket


class HostFilter(logging.Filter):
    def filter(self, record):
        record.host = socket.gethostname()
        return True
