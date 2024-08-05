"""
Different utils
"""
import time
from loguru import logger


def wait_for(func, timeout=15, period=1):
    """
    Wait for decorator
    """
    def decorator(*args, **kwargs):
        end_time = time.time() + timeout
        func_result = func(*args, **kwargs)
        while not func_result and time.time() < end_time:
            func_result = func(*args, **kwargs)
            logger.debug("wait_for: current result '{}'".format(func_result))
            time.sleep(period)
        if time.time() > end_time:
            logger.warning("{}{} not triggered within: {} sec.\nLast result was: '{}'"
                           .format(func.name, (args, kwargs), timeout, func_result))
        return func_result
    return decorator
