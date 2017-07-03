import sys
import time
import typing
import inspect
import functools

import redis

from . import static_data

REDDIT_MARKDOWN_CHARACTERS = static_data.REDDIT_MARKDOWN_CHARACTERS


class DefaultSafeDict(dict):
    """Should be used instead of dict() in string.format_map function with any
    string in contents of which you are unsure in order to escape curly
    brackets in formatted text. For example, if string contains line entered
    by user - it can possibly contain {}, which will break string.format()"""
    def __missing__(self, key):
        return '{' + key + '}'


def escape_reddit_markdown(string):
    for charater in REDDIT_MARKDOWN_CHARACTERS:
        string = string.replace(charater, '\\'+charater)
    return string


def get_string_from_countable(name, value):
    if value % 10 == 1 and value != 11:
        return f'{value} {name}'
    else:
        return f'{value} {name}s'


def logging(*triggers, out=sys.stdout):
    """Will log function if all triggers are True"""
    log = min(triggers)  # will be False if any trigger is false

    def wrapper(function):
        @functools.wraps(function)
        def wrapped_function(*args, **kwargs):
            result = function(*args, **kwargs)
            if log:
                print(function.__name__, args, kwargs, result, file=out)
            return result
        return wrapped_function

    def async_wrapper(async_function):
        @functools.wraps(async_function)
        async def wrapped_async_function(*args, **kwargs):
            result = await async_function(*args, **kwargs)
            if log:
                print(async_function.__name__, args, kwargs, result, file=out)
            return result
        return wrapped_async_function

    def cool_wrapper(function):
        is_async_function = inspect.iscoroutinefunction(function)
        if is_async_function:
            return async_wrapper(function)
        else:
            return wrapper(function)

    return cool_wrapper


# Cache function + helper functions for caching below
class TimeoutDict:
    class TimeoutValue:
        def __init__(self, value, expiration_time):
            self.value = value
            self.expiration_time = expiration_time

    def __init__(self):
        self.__dict = dict()

    def get(self, key, default=None):
        result = self.__dict.get(key, default)
        if isinstance(result, self.TimeoutValue):
            if time.time() > result.expiration_time:
                self.__dict.pop(key)
                return default
            else:
                return result.value
        else:
            return result

    def set(self, key, value):
        self.__dict[key] = value

    def setex(self, key, value, timeout):
        self.__dict[key] = self.TimeoutValue(value, time.time() + timeout)


def get_result_type(function):
    try:
        result_type = typing.get_type_hints(function)['return']
    except KeyError:
        qualname = function.__qualname__
        e = f'Cached function {qualname} lacks return type hint'
        raise ValueError(e)
    return result_type


def make_key(function, *args, **kwargs):
    name_and_args = (function.__qualname__,) + tuple(a for a in args)
    return functools._make_key(name_and_args, kwargs, False)


def cached(timeout=None, redis_url=None):
    """Requires return type hint on cached function! If used on class methods,
    make sure that class has defined __repr__ method so that in can be
    consistently represented between application restarts. Function should only
    return one data type."""
    class Function:  # Used as mutable to store data about cached function
        pass

    if redis_url:
        cache = cached.__redis_pool.setdefault(
          redis_url, redis.from_url(redis_url))
    else:
        cache = TimeoutDict()
    func = Function()

    def cached_function(*args, **kwargs):
        key = make_key(func.function, *args, **kwargs)
        cached_result = cache.get(key)
        if cached_result:
            return func.result_type(cached_result.decode('utf-8'))
        else:
            result = func.function(*args, **kwargs)
            if timeout:
                cache.setex(key, str(result).encode(), timeout)
            else:
                cache.set(key, str(result).encode(), timeout)
            return result

    async def async_cached_function(*args, **kwargs):
        key = make_key(*args, **kwargs)
        cached_result = cache.get(key)
        if cached_result:
            return func.result_type(cached_result.decode('utf-8'))
        else:
            result = await func.function(*args, **kwargs)
            if timeout:
                cache.setex(key, str(result).encode(), timeout)
            else:
                cache.set(key, str(result).encode(), timeout)
            return result

    def wrapper(function):
        func.result_type = get_result_type(function)
        func.is_async = inspect.iscoroutinefunction(function)
        func.function = function
        print(func.function, func.function.__qualname__)
        if func.is_async:
            return functools.wraps(function)(async_cached_function)
        else:
            return functools.wraps(function)(cached_function)

    return wrapper
cached.__redis_pool = dict()
