import sys
from functools import wraps, _make_key

import redis


def logging(*triggers, out=sys.stdout):
    """Will log function if all triggers are True"""
    log = min(triggers)  # will be False if any trigger is false

    def wrapper(function):
        @wraps(function)
        def wrapped_function(*args, **kwargs):
            if log:
                print('calling', function.__name__, args, kwargs, file=out)
            result = function(*args, **kwargs)
            if log:
                print('result', function.__name__, result, file=out)
            return result
        return wrapped_function
    return wrapper


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
