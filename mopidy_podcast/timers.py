from __future__ import unicode_literals

import functools
import logging
import time


class LoggingTimer(object):

    def __init__(self, logger, level, msg, timer=time.time, timeunit=1.0):
        self.logger = logger
        self.level = level
        self.msg = msg
        self.timer = timer
        self.timeunit = timeunit

    def __enter__(self):
        self.start = self.timer()

    def __exit__(self, exc_type, exc_value, traceback):
        d = (self.timer() - self.start) * self.timeunit
        self.logger.log(self.level, '%s: %.3fs', self.msg, d)


class DebugTimer(LoggingTimer):

    def __init__(self, logger, msg, timer=time.time, timeunit=1.0):
        LoggingTimer.__init__(self, logger, logging.DEBUG, msg,
                              timer, timeunit)


def debug_timer(logger, msg, timer=time.time, timeunit=1.0):
    def decorator(func):
        def wrapper(*args, **kwargs):
            with DebugTimer(logger, msg, timer, timeunit):
                return func(*args, **kwargs)
        return functools.update_wrapper(wrapper, func)
    return decorator
