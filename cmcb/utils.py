import sys
import inspect
import functools

import redis

import static_data

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


def redis_timeout_cache(redis_url, timeout):
    """If you use this cache on object methods, make sure that this object has
    a defined __repr__ so it can be consistently represented between
    application restarts."""
    def wrapper(function):
        cache = redis.from_url(redis_url)
        is_async = inspect.iscoroutinefunction(function)

        def get_cached_result(*args, **kwargs):
            name_and_args = (function.__name__,) + tuple(arg for arg in args)
            key = functools._make_key(name_and_args, kwargs, False)
            cached_result = cache.get(key)
            return key, cached_result

        @functools.wraps(function)
        def cached_function(*args, **kwargs):
            key, cached_result = get_cached_result(*args, **kwargs)
            if cached_result is not None:
                return cached_result.decode('utf-8')
            else:
                result = function(*args, **kwargs)
                cache.setex(key, result, timeout)
                return result

        @functools.wraps(function)
        async def async_cached_function(*args, **kwargs):
            key, cached_result = get_cached_result(*args, **kwargs)
            if cached_result is not None:
                return cached_result.decode('utf-8')
            else:
                result = await function(*args, **kwargs)
                cache.setex(key, result, timeout)
                return result

        if is_async:
            return async_cached_function
        else:
            return cached_function
    return wrapper
