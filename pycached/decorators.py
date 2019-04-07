import inspect
import functools
import logging

from pycached import caches, SimpleMemoryCache
from pycached.base import SENTINEL
from pycached.lock import RedLock


logger = logging.getLogger(__name__)


class cached:
    """
    Caches the functions return value into a key generated with module_name, function_name and args.
    The cache is available in the function object as ``<function_name>.cache``.

    In some cases you will need to send more args to configure the cache object.
    An example would be endpoint and port for the SimpleMemoryCache. You can send those args as
    kwargs and they will be propagated accordingly.

    Only one cache instance is created per decorated call. If you expect high concurrency of calls
    to the same function, you should adapt the pool size as needed.

    When calling the decorated function, the reads and writes from/to the cache can be controlled
    with the parameters ``cache_read`` and ``cache_write`` (both are enabled by default).

    :param ttl: int seconds to store the function call. Default is None which means no expiration.
    :param key: str value to set as key for the function return. Takes precedence over
        key_builder param. If key and key_builder are not passed, it will use module_name
        + function_name + args + kwargs
    :param key_builder: Callable that allows to build the function dynamically. It receives
        the function plus same args and kwargs passed to the function.
    :param cache: cache class to use when calling the ``set``/``get`` operations.
        Default is ``pycached.SimpleMemoryCache``.
    :param serializer: serializer instance to use when calling the ``dumps``/``loads``.
        If its None, default one from the cache backend is used.
    :param plugins: list plugins to use when calling the cmd hooks
        Default is pulled from the cache class being used.
    :param alias: str specifying the alias to load the config from. If alias is passed, other config
        parameters are ignored. Same cache identified by alias is used on every call. If you need
        a per function cache, specify the parameters explicitly without using alias.
    :param noself: bool if you are decorating a class function, by default self is also used to
        generate the key. This will result in same function calls done by different class instances
        to use different cache keys. Use noself=True if you want to ignore it.
    """

    def __init__(
        self,
        ttl=SENTINEL,
        key=None,
        key_builder=None,
        cache=SimpleMemoryCache,
        serializer=None,
        plugins=None,
        alias=None,
        noself=False,
        **kwargs
    ):
        self.ttl = ttl
        self.key = key
        self.key_builder = key_builder
        self.noself = noself
        self.alias = alias
        self.cache = None

        self._cache = cache
        self._serializer = serializer
        self._plugins = plugins
        self._kwargs = kwargs

    def __call__(self, f):
        if self.alias:
            self.cache = caches.get(self.alias)
        else:
            self.cache = _get_cache(
                cache=self._cache,
                serializer=self._serializer,
                plugins=self._plugins,
                **self._kwargs
            )

        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            return self.decorator(f, *args, **kwargs)

        wrapper.cache = self.cache
        return wrapper

    def decorator(self, f, *args, cache_read=True, cache_write=True, **kwargs):
        key = self.get_cache_key(f, args, kwargs)

        if cache_read:
            value = self.get_from_cache(key)
            if value is not None:
                return value

        result = f(*args, **kwargs)

        if cache_write:
            self.set_in_cache(key, result)

        return result

    def get_cache_key(self, f, args, kwargs):
        if self.key:
            return self.key
        if self.key_builder:
            return self.key_builder(f, *args, **kwargs)

        return self._key_from_args(f, args, kwargs)

    def _key_from_args(self, func, args, kwargs):
        ordered_kwargs = sorted(kwargs.items())
        return (
            (func.__module__ or "")
            + func.__name__
            + str(args[1:] if self.noself else args)
            + str(ordered_kwargs)
        )

    def get_from_cache(self, key):
        try:
            value = self.cache.get(key)
            return value
        except Exception:
            logger.exception("Couldn't retrieve %s, unexpected error", key)

    def set_in_cache(self, key, value):
        try:
            self.cache.set(key, value, self.ttl)
        except Exception:
            logger.exception("Couldn't set %s in key %s, unexpected error", value, key)


class cached_stampede(cached):
    """
    Caches the functions return value into a key generated with module_name, function_name and args
    while avoids for cache stampede effects.

    In some cases you will need to send more args to configure the cache object.
    An example would be endpoint and port for the SimpleMemoryCache. You can send those args as
    kwargs and they will be propagated accordingly.

    Only one cache instance is created per decorated function. If you expect high concurrency
    of calls to the same function, you should adapt the pool size as needed.

    :param lease: int seconds to lock function call to avoid cache stampede effects.
        If 0 or None, no locking happens (default is 2). redis and memory backends support
        float ttls
    :param ttl: int seconds to store the function call. Default is None which means no expiration.
    :param key: str value to set as key for the function return. Takes precedence over
        key_from_attr param. If key and key_from_attr are not passed, it will use module_name
        + function_name + args + kwargs
    :param key_from_attr: str arg or kwarg name from the function to use as a key.
    :param cache: cache class to use when calling the ``set``/``get`` operations.
        Default is ``pycached.SimpleMemoryCache``.
    :param serializer: serializer instance to use when calling the ``dumps``/``loads``.
        Default is JsonSerializer.
    :param plugins: list plugins to use when calling the cmd hooks
        Default is pulled from the cache class being used.
    :param alias: str specifying the alias to load the config from. If alias is passed, other config
        parameters are ignored. New cache is created every time.
    :param noself: bool if you are decorating a class function, by default self is also used to
        generate the key. This will result in same function calls done by different class instances
        to use different cache keys. Use noself=True if you want to ignore it.
    """

    def __init__(self, lease=2, **kwargs):
        super().__init__(**kwargs)
        self.lease = lease

    def decorator(self, f, *args, **kwargs):
        key = self.get_cache_key(f, args, kwargs)

        value = self.get_from_cache(key)
        if value is not None:
            return value

        with RedLock(self.cache, key, self.lease):
            value = self.get_from_cache(key)
            if value is not None:
                return value

            result = f(*args, **kwargs)

            self.set_in_cache(key, result)

        return result


def _get_cache(cache=SimpleMemoryCache, serializer=None, plugins=None, **cache_kwargs):
    return cache(serializer=serializer, plugins=plugins, **cache_kwargs)


def _get_args_dict(func, args, kwargs):
    defaults = {
        arg_name: arg.default
        for arg_name, arg in inspect.signature(func).parameters.items()
        if arg.default is not inspect._empty  # TODO: bug prone..
    }
    args_names = func.__code__.co_varnames[: func.__code__.co_argcount]
    return {**defaults, **dict(zip(args_names, args)), **kwargs}


class multi_cached:
    """
    Only supports functions that return dict-like structures. This decorator caches each key/value
    of the dict-like object returned by the function.
    The cache is available in the function object as ``<function_name>.cache``.

    If key_builder is passed, before storing the key, it will be transformed according to the output
    of the function.

    If the attribute specified to be the key is an empty list, the cache will be ignored and
    the function will be called as expected.

    Only one cache instance is created per decorated function. If you expect high concurrency
    of calls to the same function, you should adapt the pool size as needed.

    When calling the decorated function, the reads and writes from/to the cache can be controlled
    with the parameters ``cache_read`` and ``cache_write`` (both are enabled by default).

    :param keys_from_attr: arg or kwarg name from the function containing an iterable to use
        as keys to index in the cache.
    :param key_builder: Callable that allows to change the format of the keys before storing.
        Receives the key the function and same args and kwargs as the called function.
    :param ttl: int seconds to store the keys. Default is 0 which means no expiration.
    :param cache: cache class to use when calling the ``multi_set``/``multi_get`` operations.
        Default is ``pycached.SimpleMemoryCache``.
    :param serializer: serializer instance to use when calling the ``dumps``/``loads``.
        If its None, default one from the cache backend is used.
    :param plugins: plugins to use when calling the cmd hooks
        Default is pulled from the cache class being used.
    :param alias: str specifying the alias to load the config from. If alias is passed, other config
        parameters are ignored. Same cache identified by alias is used on every call. If you need
        a per function cache, specify the parameters explicitly without using alias.
    """

    def __init__(
        self,
        keys_from_attr,
        key_builder=None,
        ttl=SENTINEL,
        cache=SimpleMemoryCache,
        serializer=None,
        plugins=None,
        alias=None,
        **kwargs
    ):
        self.keys_from_attr = keys_from_attr
        self.key_builder = key_builder or (lambda key, f, *args, **kwargs: key)
        self.ttl = ttl
        self.alias = alias
        self.cache = None

        self._cache = cache
        self._serializer = serializer
        self._plugins = plugins
        self._kwargs = kwargs

    def __call__(self, f):
        if self.alias:
            self.cache = caches.get(self.alias)
        else:
            self.cache = _get_cache(
                cache=self._cache,
                serializer=self._serializer,
                plugins=self._plugins,
                **self._kwargs
            )

        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            return self.decorator(f, *args, **kwargs)

        wrapper.cache = self.cache
        return wrapper

    def decorator(self, f, *args, cache_read=True, cache_write=True, **kwargs):
        missing_keys = []
        partial = {}
        keys, new_args, args_index = self.get_cache_keys(f, args, kwargs)

        if cache_read:
            values = self.get_from_cache(*keys)
            for key, value in zip(keys, values):
                if value is None:
                    missing_keys.append(key)
                else:
                    partial[key] = value
            if values and None not in values:
                return partial
        else:
            missing_keys = list(keys)

        if args_index > -1:
            new_args[args_index] = missing_keys
        else:
            kwargs[self.keys_from_attr] = missing_keys

        result = f(*new_args, **kwargs)
        result.update(partial)

        if cache_write:
            self.set_in_cache(result, f, args, kwargs)

        return result

    def get_cache_keys(self, f, args, kwargs):
        args_dict = _get_args_dict(f, args, kwargs)
        keys = args_dict[self.keys_from_attr] or []
        keys = [self.key_builder(key, f, *args, **kwargs) for key in keys]

        args_names = f.__code__.co_varnames[: f.__code__.co_argcount]
        new_args = list(args)
        keys_index = -1
        if self.keys_from_attr in args_names and self.keys_from_attr not in kwargs:
            keys_index = args_names.index(self.keys_from_attr)
            new_args[keys_index] = keys

        return keys, new_args, keys_index

    def get_from_cache(self, *keys):
        if not keys:
            return []
        try:
            values = self.cache.multi_get(keys)
            return values
        except Exception:
            logger.exception("Couldn't retrieve %s, unexpected error", keys)
            return [None] * len(keys)

    def set_in_cache(self, result, fn, fn_args, fn_kwargs):
        try:
            self.cache.multi_set(
                [(self.key_builder(k, fn, *fn_args, **fn_kwargs), v) for k, v in result.items()],
                ttl=self.ttl,
            )
        except Exception:
            logger.exception("Couldn't set %s, unexpected error", result)