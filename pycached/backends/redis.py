import functools
import itertools

import redis

from pycached.base import BaseCache
from pycached.serializers import JsonSerializer

REDIS_BEFORE_ONE = redis.__version__.startswith("2.")


def conn(func):
    @functools.wraps(func)
    def wrapper(self, *args, _conn=None, **kwargs):
        if _conn is None:
            _conn = self._get_pool()
        return func(self, *args, _conn=_conn, **kwargs)

    return wrapper


class RedisBackend:
    RELEASE_SCRIPT = (
        "if redis.call('get',KEYS[1]) == ARGV[1] then"
        " return redis.call('del',KEYS[1])"
        " else"
        " return 0"
        " end"
    )

    CAS_SCRIPT = (
        "if redis.call('get',KEYS[1]) == ARGV[2] then"
        "  if #ARGV == 4 then"
        "   return redis.call('set', KEYS[1], ARGV[1], ARGV[3], ARGV[4])"
        "  else"
        "   return redis.call('set', KEYS[1], ARGV[1])"
        "  end"
        " else"
        " return 0"
        " end"
    )

    def __init__(
            self,
            endpoint="127.0.0.1",
            port=6379,
            db=0,
            password=None,
            max_connections=10,
            loop=None,
            create_connection_timeout=None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.endpoint = endpoint
        self.port = port
        self.db = db
        self.password = password
        self.max_connections = max_connections
        self.create_connection_timeout = create_connection_timeout
        self._loop = loop
        self._pool = None

    def _get_pool(self):
        if self._pool is None:
            kwargs = {
                "host": self.endpoint,
                "port": self.port,
                "db": self.db,
                "password": self.password,
                "connection_pool": self._loop,
                "encoding": "utf-8",
                "decode_responses": True,
                "max_connections": self.max_connections,
            }
            self._pool = redis.Redis(**kwargs)

        return self._pool

    def _close(self, *args, **kwargs):
        pass

    def acquire_conn(self):
        return self._get_pool()

    def release_conn(self, _conn):
        pass

    @conn
    def _get(self, key, _conn=None):
        return _conn.get(key)

    @conn
    def _gets(self, key, _conn=None):
        return self._get(key, _conn=_conn)

    @conn
    def _multi_get(self, keys, _conn=None):
        return _conn.mget(*keys)

    @conn
    def _set(self, key, value, ttl=None, _cas_token=None, _conn=None):
        if _cas_token is not None:
            return self._cas(key, value, _cas_token, ttl=ttl, _conn=_conn)
        if ttl is None:
            return _conn.set(key, value)
        if REDIS_BEFORE_ONE:
            return _conn.setex(key, value, ttl)
        return _conn.setex(key, ttl, value)

    @conn
    def _cas(self, key, value, token, ttl=None, _conn=None):
        args = [value, token]
        if ttl is not None:
            if isinstance(ttl, float):
                args += ["PX", int(ttl * 1000)]
            else:
                args += ["EX", ttl]
        res = self._raw("eval", self.CAS_SCRIPT, [key], args, _conn=_conn)
        return res

    @conn
    def _multi_set(self, pairs, ttl=None, _conn=None):
        ttl = ttl or 0

        flattened = list(itertools.chain.from_iterable((key, value) for key, value in pairs))

        if ttl:
            self.__multi_set_ttl(_conn, flattened, ttl)
        else:
            _conn.mset(*flattened)

        return True

    def __multi_set_ttl(self, conn, flattened, ttl):
        redis = conn.multi_exec()
        redis.mset(*flattened)
        for key in flattened[::2]:
            redis.expire(key, timeout=ttl)
        redis.execute()

    @conn
    def _add(self, key, value, ttl=None, _conn=None):
        expx = {"expire": ttl}
        if isinstance(ttl, float):
            expx = {"pexpire": int(ttl * 1000)}
        was_set = _conn.set(key, value, exist=_conn.SET_IF_NOT_EXIST, **expx)
        if not was_set:
            raise ValueError("Key {} already exists, use .set to update the value".format(key))
        return was_set

    @conn
    def _exists(self, key, _conn=None):
        exists = _conn.exists(key)
        return True if exists > 0 else False

    @conn
    def _increment(self, key, delta, _conn=None):
        try:
            return _conn.incrby(key, delta)
        except redis.errors.ReplyError:
            raise TypeError("Value is not an integer") from None

    @conn
    def _expire(self, key, ttl, _conn=None):
        if ttl == 0:
            return _conn.persist(key)
        return _conn.expire(key, ttl)

    @conn
    def _delete(self, key, _conn=None):
        return _conn.delete(key)

    @conn
    def _clear(self, namespace=None, _conn=None):
        if namespace:
            keys = _conn.keys("{}:*".format(namespace))
            _conn.delete(*keys)
        else:
            _conn.flushdb()
        return True

    @conn
    def _raw(self, command, *args, _conn=None, **kwargs):
        return getattr(_conn, command)(*args, **kwargs)

    def _redlock_release(self, key, value):
        return self._raw("eval", self.RELEASE_SCRIPT, [key], [value])


class RedisCache(RedisBackend, BaseCache):
    """
    Redis cache implementation with the following components as defaults:
        - serializer: :class:`pycached.serializers.JsonSerializer`
        - plugins: []

    Config options are:

    :param serializer: obj derived from :class:`pycached.serializers.BaseSerializer`.
    :param plugins: list of :class:`pycached.plugins.BasePlugin` derived classes.
    :param namespace: string to use as default prefix for the key used in all operations of
        the backend. Default is None.
    :param timeout: int or float in seconds specifying maximum timeout for the operations to last.
        By default its 5.
    :param endpoint: str with the endpoint to connect to. Default is "127.0.0.1".
    :param port: int with the port to connect to. Default is 6379.
    :param db: int indicating database to use. Default is 0.
    :param password: str indicating password to use. Default is None.
    :param pool_min_size: int minimum pool size for the redis connections pool. Default is 1
    :param pool_max_size: int maximum pool size for the redis connections pool. Default is 10
    :param create_connection_timeout: int timeout for the creation of connection,
        only for redis>=1. Default is None
    """

    def __init__(self, serializer=None, **kwargs):
        super().__init__(**kwargs)
        self.serializer = serializer or JsonSerializer()

    def _build_key(self, key, namespace=None):
        if namespace is not None:
            return "{}{}{}".format(namespace, ":" if namespace else "", key)
        if self.namespace is not None:
            return "{}{}{}".format(self.namespace, ":" if self.namespace else "", key)
        return key

    def __repr__(self):  # pragma: no cover
        return "RedisCache ({}:{})".format(self.endpoint, self.port)
