from collections import namedtuple

from pycached import RedisCache
from pycached.serializers import PickleSerializer

MyObject = namedtuple("MyObject", ["x", "y"])
cache = RedisCache(serializer=PickleSerializer(), namespace="main")


def complex_object():
    obj = MyObject(x=1, y=2)
    cache.set("key", obj)
    my_object = cache.get("key")

    assert my_object.x == 1
    assert my_object.y == 2


def test_python_object():
    complex_object()
    cache.delete("key")
    cache.close()


if __name__ == "__main__":
    test_python_object()
