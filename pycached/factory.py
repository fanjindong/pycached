import urllib
import warnings
from copy import deepcopy

from pycached import CACHE_CACHES
from pycached.exceptions import InvalidCacheType


def _class_from_string(class_path):
    class_name = class_path.split(".")[-1]
    module_name = class_path.rstrip(class_name).rstrip(".")
    return getattr(__import__(module_name, fromlist=[class_name]), class_name)


def _create_cache(cache, serializer=None, plugins=None, **kwargs):
    if serializer is not None:
        cls = serializer.pop("class")
        cls = _class_from_string(cls) if isinstance(cls, str) else cls
        serializer = cls(**serializer)

    plugins_instances = []
    if plugins is not None:
        for plugin in plugins:
            cls = plugin.pop("class")
            cls = _class_from_string(cls) if isinstance(cls, str) else cls
            plugins_instances.append(cls(**plugin))

    cache = _class_from_string(cache) if isinstance(cache, str) else cache
    instance = cache(serializer=serializer, plugins=plugins_instances, **kwargs)
    return instance


class Cache:
    """
    This class is just a proxy to the specific cache implementations like
    :class:`pycached.SimpleMemoryCache`, :class:`pycached.RedisCache` and
    :class:`pycached.MemcachedCache`. It is the preferred method of
    instantiating new caches over using the backend specific classes.

    You can instatiate a new one using the ``cache_type`` attribute like:
    >>> from pycached import Cache
    >>> Cache(Cache.REDIS)
    RedisCache (127.0.0.1:6379)

    If you don't specify anything, ``Cache.MEMORY`` is used.
    Only ``Cache.MEMORY``, ``Cache.REDIS`` and ``Cache.MEMCACHED`` types
    are allowed. If the type passed is invalid, it will raise a
    :class:`pycached.exceptions.InvalidCacheType` exception.
    """

    MEMORY = "memory"
    REDIS = "redis"

    def __new__(cls, cache_type=MEMORY, **kwargs):
        cache_class = cls.get_scheme_class(cache_type)
        instance = cache_class.__new__(cache_class, **kwargs)
        instance.__init__(**kwargs)
        return instance

    @classmethod
    def get_scheme_class(cls, scheme):
        try:
            return CACHE_CACHES[scheme]
        except KeyError as e:
            raise InvalidCacheType(
                "Invalid cache type, you can only use {}".format(list(CACHE_CACHES.keys()))
            ) from e

    @classmethod
    def from_url(cls, url):
        """
        Given a resource uri, return an instance of that cache initialized with the given
        parameters. An example usage:

        >>> from pycached import Cache
        >>> Cache.from_url('memory://')
        <pycached.backends.memory.SimpleMemoryCache object at 0x1081dbb00>
        a more advanced usage using queryparams to configure the cache:
        >>> from pycached import Cache
        >>> cache = Cache.from_url('redis://localhost:10/1?pool_min_size=1')
        >>> cache
        RedisCache (localhost:10)
        >>> cache.db
        1
        >>> cache.pool_min_size
        1

        :param url: string identifying the resource uri of the cache to connect to
        """

        parsed_url = urllib.parse.urlparse(url)
        kwargs = dict(urllib.parse.parse_qsl(parsed_url.query))

        if parsed_url.path:
            kwargs.update(Cache.get_scheme_class(parsed_url.scheme).parse_uri_path(parsed_url.path))

        if parsed_url.hostname:
            kwargs["endpoint"] = parsed_url.hostname

        if parsed_url.port:
            kwargs["port"] = parsed_url.port

        if parsed_url.password:
            kwargs["password"] = parsed_url.password

        return Cache(parsed_url.scheme, **kwargs)


class CacheHandler:
    _config = {
        "default": {
            "cache": "pycached.SimpleMemoryCache",
            "serializer": {"class": "pycached.serializers.StringSerializer"},
        }
    }

    def __init__(self):
        self._caches = {}

    def add(self, alias: str, config: dict) -> None:
        """
        Add a cache to the current config. If the key already exists, it
        will overwrite it::

            >>> caches.add('default', {
                    'cache': "aiocache.SimpleMemoryCache",
                    'serializer': {
                        'class': "aiocache.serializers.StringSerializer"
                    }
                })

        :param alias: The alias for the cache
        :param config: Mapping containing the cache configuration
        """
        self._config[alias] = config

    def get(self, alias):
        """
        Retrieve cache identified by alias. Will return always the same instance

        If the cache was not instantiated yet, it will do it lazily the first time
        this is called.

        :param alias: str cache alias
        :return: cache instance
        """
        try:
            return self._caches[alias]
        except KeyError:
            pass

        config = self.get_alias_config(alias)
        cache = _create_cache(**deepcopy(config))
        self._caches[alias] = cache
        return cache

    def create(self, alias=None, cache=None, **kwargs):
        """
        Create a new cache. Either alias or cache params are required. You can use
        kwargs to pass extra parameters to configure the cache.

        .. deprecated:: 0.11.0
            Only creating a cache passing an alias is supported. If you want to
            create a cache passing explicit cache and kwargs use ``pycached.Cache``.

        :param alias: str alias to pull configuration from
        :param cache: str or class cache class to use for creating the
            new cache (when no alias is used)
        :return: New cache instance
        """
        if alias:
            config = self.get_alias_config(alias)
        elif cache:
            warnings.warn(
                "Creating a cache with an explicit config is deprecated, use 'pycached.Cache'",
                DeprecationWarning,
            )
            config = {"cache": cache}
        else:
            raise TypeError("create call needs to receive an alias or a cache")
        cache = _create_cache(**{**config, **kwargs})
        return cache

    def get_alias_config(self, alias):
        config = self.get_config()
        if alias not in config:
            raise KeyError(
                "Could not find config for '{0}', ensure you include {0} when calling"
                "caches.set_config specifying the config for that cache".format(alias)
            )

        return config[alias]

    def get_config(self):
        """
        Return copy of current stored config
        """
        return deepcopy(self._config)

    def set_config(self, config):
        """
        Set (override) the default config for cache aliases from a dict-like structure.
        The structure is the following::

            {
                'default': {
                    'cache': "pycached.SimpleMemoryCache",
                    'serializer': {
                        'class': "pycached.serializers.StringSerializer"
                    }
                },
                'redis_alt': {
                    'cache': "pycached.RedisCache",
                    'endpoint': "127.0.0.10",
                    'port': 6378,
                    'serializer': {
                        'class': "pycached.serializers.PickleSerializer"
                    },
                    'plugins': [
                        {'class': "pycached.plugins.HitMissRatioPlugin"},
                        {'class': "pycached.plugins.TimingPlugin"}
                    ]
                }
            }

        'default' key must always exist when passing a new config. Default configuration
        is::

            {
                'default': {
                    'cache': "pycached.SimpleMemoryCache",
                    'serializer': {
                        'class': "pycached.serializers.StringSerializer"
                    }
                }
            }

        You can set your own classes there.
        The class params accept both str and class types.

        All keys in the config are optional, if they are not passed the defaults
        for the specified class will be used.

        If a config key already exists, it will be updated with the new values.
        """
        if "default" not in config:
            raise ValueError("default config must be provided")
        for config_name in config.keys():
            self._caches.pop(config_name, None)
        self._config = config


caches = CacheHandler()
