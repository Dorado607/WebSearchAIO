#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import warnings
from functools import wraps
from func_timeout import func_set_timeout


def timer(time_limit: float = 5, convey: bool = False):
    """
    compute time cost
    :param time_limit: warn if func run time surpass the limit
    :param convey: output time cost as an arg if True
    """

    def deco_timer(func):
        @wraps(func)
        def clocked(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            time_cost = time.time() - start_time
            print("func (" + func.__name__ + ") costs {:.4f}s".format(time_cost))
            if time_cost > time_limit: warnings.warn(f"func_{func.__name__} took over {time_limit}s to run")
            if convey:
                return time_cost, result
            else:
                return result

        return clocked

    return deco_timer

def atimer(time_limit: float = 5, convey: bool = False):
    """
    compute time cost
    :param time_limit: warn if func run time surpass the limit
    :param convey: output time cost as an arg if True
    """

    def deco_timer(func):
        @wraps(func)
        async def clocked(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            time_cost = time.time() - start_time
            print("func (" + func.__name__ + ") costs {:.4f}s".format(time_cost))
            if time_cost > time_limit: warnings.warn(f"func_{func.__name__} took over {time_limit}s to run")
            if convey:
                return time_cost, result
            else:
                return result

        return clocked

    return deco_timer

def retry(ExceptionToCheck, max_try: int = 3, step: float = 3.0):
    """
    retry func
    :param ExceptionToCheck: exception filter, check every exception if not given
    :param max_try: try to run the func for given times
    :param step: sleep for given seconds to avoid error
    """

    def deco_retry(func):
        @wraps(func)
        def f_retry(*args, **kwargs):
            c_tries, c_step = max_try, step
            while c_tries > 0:
                try:
                    return func(*args, **kwargs)
                except ExceptionToCheck:
                    print("func:" + func.__name__ + " retrying for:{}/{}".format(max_try - c_tries + 1, max_try))
                    c_tries -= 1
                    time.sleep(c_step)
                    raise ExceptionToCheck
            return func(*args, **kwargs)

        return f_retry

    return deco_retry
