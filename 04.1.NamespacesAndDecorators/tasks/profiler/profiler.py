import functools
from datetime import datetime


def profiler(func):  # type: ignore
    """
    Returns profiling decorator, which counts calls of function
    and measure last function execution time.
    Results are stored as function attributes: `calls`, `last_time_taken`
    :param func: function to decorate
    :return: decorator, which wraps any function passed
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):  # type: ignore
        if wrapper.rec_calls == 0:
            wrapper.calls = 0
            wrapper.time_begin = datetime.now()
        wrapper.rec_calls += 1
        wrapper.calls += 1
        result = func(*args, **kwargs)
        wrapper.rec_calls -= 1
        if wrapper.rec_calls == 0:
            time_begin = wrapper.time_begin
            time_end = datetime.now()
            wrapper.last_time_taken = (time_end - time_begin).total_seconds()
            print(f'{wrapper.calls=}, {wrapper.last_time_taken=}')
        return result

    wrapper.rec_calls = 0
    wrapper.time_begin = datetime.now()
    wrapper.calls = None
    wrapper.last_time_taken = None
    return wrapper
