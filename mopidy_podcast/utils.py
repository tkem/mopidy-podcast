from __future__ import unicode_literals

import time


class DebugTimer(object):

    def __init__(self, logger, msg):
        self.logger = logger
        self.msg = msg
        self.start = None

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, exc_type, exc_value, traceback):
        duration = (time.time() - self.start) * 1000
        self.logger.debug('%s took %dms', self.msg, duration)
