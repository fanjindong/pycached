import logging

from .backends import RedisCache,SimpleMemoryCache
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



from .factory import caches, Cache  # noqa: E402
from .decorators import cached, cached_stampede, multi_cached  # noqa: E402


__all__ = (
    "caches",
    "Cache",
    "cached",
    "cached_stampede",
    "multi_cached",
    *__cache_types,
    "__version__",
)