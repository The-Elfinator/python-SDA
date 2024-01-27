import functools
from collections import OrderedDict
from collections.abc import Callable
from typing import Any, TypeVar, ParamSpec

T = TypeVar("T")
P = ParamSpec("P")
Function = TypeVar('Function', bound=Callable[..., Any])


def cache(max_size: int) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Returns decorator, which stores result of function
    for `max_size` most recent function arguments.
    :param max_size: max amount of unique arguments to store values for
    :return: decorator, which wraps any function passed
    """

    def inner(func: Callable[P, T]) -> Callable[P, T]:
        my_cache: OrderedDict[str, T] = OrderedDict()

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            cache_key = str(args + tuple(kwargs.items()))
            if cache_key not in my_cache:
                size = len(my_cache)
                if size == max_size:
                    my_cache.popitem(last=False)
                cache_value = func(*args, **kwargs)
                my_cache[cache_key] = cache_value
            return my_cache[cache_key]

        return wrapper

    return inner
