import logging

from .backends import RedisCache,SimpleMemoryCache
from .factory import caches
from .decorators import cached, cached_stampede, multi_cached
from ._version import __version__


logger = logging.getLogger(__name__)
__cache_types = [RedisCache]

try:
    import redis
except ImportError:
    logger.info("redis not installed, RedisCache unavailable")
else:
    from pycached.backends.redis import RedisCache

    __cache_types.append(RedisCache)
    del redis



__all__ = ("caches", "cached", "cached_stampede", "multi_cached", *__cache_types, "__version__")
