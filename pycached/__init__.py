import logging

from ._version import __version__
from .backends import RedisCache, SimpleMemoryCache

logger = logging.getLogger(__name__)
CACHE_CACHES = {"memory": SimpleMemoryCache}

try:
    import redis
except ImportError:
    logger.info("redis not installed, RedisCache unavailable")
else:
    from pycached.backends.redis import RedisCache

    CACHE_CACHES["redis"] = RedisCache
    del redis

from .factory import caches, Cache  # noqa: E402
from .decorators import cached, cached_stampede, multi_cached  # noqa: E402

__all__ = (
    "caches",
    "Cache",
    "cached",
    "cached_stampede",
    "multi_cached",
    *list(CACHE_CACHES.values()),
    "__version__",
)
