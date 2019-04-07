import logging
import random

from pycached import SimpleMemoryCache
from pycached.plugins import HitMissRatioPlugin, TimingPlugin, BasePlugin

logger = logging.getLogger(__name__)


class MyCustomPlugin(BasePlugin):

    def pre_set(self, *args, **kwargs):
        logger.info("I'm the pre_set hook being called with %s %s" % (args, kwargs))

    def post_set(self, *args, **kwargs):
        logger.info("I'm the post_set hook being called with %s %s" % (args, kwargs))


cache = SimpleMemoryCache(
    plugins=[HitMissRatioPlugin(), TimingPlugin(), MyCustomPlugin()],
    namespace="main")


def run():
    cache.set("a", "1")
    cache.set("b", "2")
    cache.set("c", "3")
    cache.set("d", "4")

    possible_keys = ["a", "b", "c", "d", "e", "f"]

    for t in range(1000):
        cache.get(random.choice(possible_keys))

    assert cache.hit_miss_ratio["hit_ratio"] > 0.5
    assert cache.hit_miss_ratio["total"] == 1000

    assert cache.profiling["get_min"] > 0
    assert cache.profiling["set_min"] > 0
    assert cache.profiling["get_max"] > 0
    assert cache.profiling["set_max"] > 0

    print(cache.hit_miss_ratio)
    print(cache.profiling)


def test_run():
    run()
    cache.delete("a")
    cache.delete("b")
    cache.delete("c")
    cache.delete("d")

if __name__ == "__main__":
    test_run()
