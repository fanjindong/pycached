import zlib

from pycached import Cache
from pycached.serializers import BaseSerializer


class CompressionSerializer(BaseSerializer):

    # This is needed because zlib works with bytes.
    # this way the underlying backend knows how to
    # store/retrieve values
    DEFAULT_ENCODING = None

    def dumps(self, value):
        print("I've received:\n{}".format(value))
        compressed = zlib.compress(value.encode())
        print("But I'm storing:\n{}".format(compressed))
        return compressed

    def loads(self, value):
        print("I've retrieved:\n{}".format(value))
        decompressed = zlib.decompress(value).decode()
        print("But I'm returning:\n{}".format(decompressed))
        return decompressed


cache = Cache(Cache.REDIS, serializer=CompressionSerializer(), namespace="main")


def serializer():
    text = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt"
        "ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation"
        "ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in"
        "reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur"
        "sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit"
        "anim id est laborum.")
    cache.set("key", text)
    print("-----------------------------------")
    real_value = cache.get("key")
    compressed_value = cache.raw("get", "main:key")
    assert len(compressed_value) < len(real_value.encode())


def test_serializer():
    serializer()
    cache.delete("key")
    cache.close()


if __name__ == "__main__":
    test_serializer()
