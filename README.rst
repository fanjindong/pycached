pycached
########

cache supporting multiple backends (memory, redis).
Synchronization library based on aiocache.

.. image:: https://travis-ci.org/fanjindong/pycached.svg?branch=master
  :target: https://travis-ci.org/fanjindong/pycached

.. image:: https://codecov.io/gh/fanjindong/pycached/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/fanjindong/pycached

.. image:: https://badge.fury.io/py/pycached.svg
  :target: https://pypi.python.org/pypi/pycached

.. image:: https://img.shields.io/pypi/pyversions/pycached.svg
  :target: https://pypi.python.org/pypi/pycached

.. image:: https://api.codacy.com/project/badge/Grade/96f772e38e63489ca884dbaf6e9fb7fd
  :target: https://www.codacy.com/app/fanjindong/pycached

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/ambv/black

This library aims for simplicity over specialization. All caches contain the same minimum interface which consists on the following functions:

- ``add``: Only adds key/value if key does not exist.
- ``get``: Retrieve value identified by key.
- ``set``: Sets key/value.
- ``multi_get``: Retrieves multiple key/values.
- ``multi_set``: Sets multiple key/values.
- ``exists``: Returns True if key exists False otherwise.
- ``increment``: Increment the value stored in the given key.
- ``delete``: Deletes key and returns number of deleted items.
- ``clear``: Clears the items stored.
- ``raw``: Executes the specified command using the underlying client.


.. role:: python(code)
  :language: python

.. contents::

.. section-numbering:


Installing
==========

- ``pip install pycached``
- ``pip install pycached[redis]``
- ``pip install pycached[msgpack]``


Usage
=====

Using a cache is as simple as

.. code-block:: python

    >>> from pycached import SimpleMemoryCache  # Here you can also use RedisCache and MemcachedCache
    >>> cache = SimpleMemoryCache()
    >>> cache.set('key', 'value')
    True
    >>> cache.get('key')
    'value'

Or as a decorator

.. code-block:: python

    import time

    from collections import namedtuple

    from pycached import cached, RedisCache
    from pycached.serializers import PickleSerializer
    # With this we can store python objects in backends like Redis!

    Result = namedtuple('Result', "content, status")


    @cached(ttl=10, cache=RedisCache, key="key", serializer=PickleSerializer(), port=6379, namespace="main")
    def cached_call():
        print("Sleeping for three seconds zzzz.....")
        time.sleep(3)
        return Result("content", 200)


    def run():
        cached_call()
        cached_call()
        cached_call()
        cache = RedisCache(endpoint="127.0.0.1", port=6379, namespace="main")
        cache.delete("key")

    if __name__ == "__main__":
        run()


You can also setup cache aliases so its easy to reuse configurations

.. code-block:: python

  import asyncio

  from pycached import caches, SimpleMemoryCache, RedisCache
  from pycached.serializers import StringSerializer, PickleSerializer

  # You can use either classes or strings for referencing classes
  caches.set_config({
      'default': {
          'cache': "pycached.SimpleMemoryCache",
          'serializer': {
              'class': "pycached.serializers.StringSerializer"
          }
      },
      'redis_alt': {
          'cache': "pycached.RedisCache",
          'endpoint': "127.0.0.1",
          'port': 6379,
          'timeout': 1,
          'serializer': {
              'class': "pycached.serializers.PickleSerializer"
          },
          'plugins': [
              {'class': "pycached.plugins.HitMissRatioPlugin"},
              {'class': "pycached.plugins.TimingPlugin"}
          ]
      }
  })


  def default_cache():
      cache = caches.get('default')   # This always returns the SAME instance
      cache.set("key", "value")
      assert cache.get("key") == "value"


  def alt_cache():
      cache = caches.create('redis_alt')   # This creates a NEW instance on every call
      cache.set("key", "value")
      assert cache.get("key") == "value"


  def test_alias():
      default_cache()
      alt_cache()

      caches.get('redis_alt').delete("key")


  if __name__ == "__main__":
      test_alias()


How does it work
================

Pycached provides 3 main entities:

- **backends**: Allow you specify which backend you want to use for your cache. Currently supporting: SimpleMemoryCache, RedisCache using redis_.
- **serializers**: Serialize and deserialize the data between your code and the backends. This allows you to save any Python object into your cache. Currently supporting: StringSerializer, PickleSerializer, JsonSerializer, and MsgPackSerializer. But you can also build custom ones.
- **plugins**: Implement a hooks system that allows to execute extra behavior before and after of each command.

 If you are missing an implementation of backend, serializer or plugin you think it could be interesting for the package, do not hesitate to open a new issue.

.. image:: docs/images/architecture.png
  :align: center

Those 3 entities combine during some of the cache operations to apply the desired command (backend), data transformation (serializer) and pre/post hooks (plugins). To have a better vision of what happens, here you can check how ``set`` function works in ``pycached``:

.. image:: docs/images/set_operation_flow.png
  :align: center


Amazing examples
================

In `examples folder <https://github.com/fanjindong/pycached/tree/master/examples>`_ you can check different use cases:

- `Sanic, Aiohttp and Tornado <https://github.com/fanjindong/pycached/tree/master/examples/frameworks>`_
- `Python object in Redis <https://github.com/fanjindong/pycached/blob/master/examples/python_object.py>`_
- `Custom serializer for compressing data <https://github.com/fanjindong/pycached/blob/master/examples/serializer_class.py>`_
- `TimingPlugin and HitMissRatioPlugin demos <https://github.com/fanjindong/pycached/blob/master/examples/plugins.py>`_
- `Using marshmallow as a serializer <https://github.com/fanjindong/pycached/blob/master/examples/marshmallow_serializer_class.py>`_
- `Using cached decorator <https://github.com/fanjindong/pycached/blob/master/examples/cached_decorator.py>`_.
- `Using multi_cached decorator <https://github.com/fanjindong/pycached/blob/master/examples/multicached_decorator.py>`_.



Documentation
=============

- `Usage <http://pycached.readthedocs.io/en/latest>`_
- `Caches <http://pycached.readthedocs.io/en/latest/caches.html>`_
- `Serializers <http://pycached.readthedocs.io/en/latest/serializers.html>`_
- `Plugins <http://pycached.readthedocs.io/en/latest/plugins.html>`_
- `Configuration <http://pycached.readthedocs.io/en/latest/configuration.html>`_
- `Decorators <http://pycached.readthedocs.io/en/latest/decorators.html>`_
- `Testing <http://pycached.readthedocs.io/en/latest/testing.html>`_
- `Examples <https://github.com/fanjindong/pycached/tree/master/examples>`_


.. _redis: https://github.com/andymccurdy/redis-py
