import sys
import inspect
from functools import wraps, _make_key

import redis

import static_data


class DefaultSafeDict:
    """Should be used instead of dict() in string.format_map function with any
    string in contents of which you are unsure in order to escape curly
    brackets in formatted text. For example, if string contains line, entered
    by user - it can possibly contain {}, which will break string.format()"""
    def __missing__(self, key):
        return '{' + key + '}'


def escape_reddit_markdown(string):
    for charater in static_data.REDDIT_MARKDOWN_CHARACTERS:
        string = string.replace(charater, '\\'+charater)
    return string


def logging(*triggers, out=sys.stdout):
    """Will log function if all triggers are True"""
    log = min(triggers)  # will be False if any trigger is false

    def wrapper(function):
        @wraps(function)
        def wrapped_function(*args, **kwargs):
            result = function(*args, **kwargs)
            if log:
                print(function.__name__, args, kwargs, result, file=out)
            return result
        return wrapped_function

    def async_wrapper(async_function):
        @wraps(async_function)
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


def redis_timeout_async_method_cache(timeout, redis_url):
    def wrapper(async_method):
        cache = redis.from_url(redis_url)

        @wraps(async_method)
        async def wrapped_method(self, *args, **kwargs):
            name_and_args = (async_method.__name__,) + tuple(a for a in args)
            key = _make_key(name_and_args, kwargs, False)
            cached_result = cache.get(key)
            if cached_result is not None:
                return cached_result.decode('utf-8')
            result = await async_method(self, *args, **kwargs)
            cache.setex(key, result, timeout)
            return result
        return wrapped_method
    return wrapper
