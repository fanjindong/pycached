import json

from marshmallow import Schema, fields, post_load

from pycached import Cache


class MyType:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class MyTypeSchema(Schema):
    x = fields.Number()
    y = fields.Number()

    @post_load
    def build_object(self, data):
        return MyType(data['x'], data['y'])


def dumps(value):
    return MyTypeSchema().dumps(value).data


def loads(value):
    return MyTypeSchema().loads(value).data


cache = Cache(Cache.REDIS, namespace="main")


def serializer_function():
    cache.set("key", MyType(1, 2), dumps_fn=dumps)

    obj = cache.get("key", loads_fn=loads)

    assert obj.x == 1
    assert obj.y == 2
    assert cache.get("key") == json.loads(('{"y": 2.0, "x": 1.0}'))
    assert json.loads(cache.raw("get", "main:key")) == {"y": 2.0, "x": 1.0}


def test_serializer_function():
    serializer_function()
    cache.delete("key")
    cache.close()


if __name__ == "__main__":
    test_serializer_function()
