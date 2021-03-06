.. pycached documentation master file, created by
   sphinx-quickstart on Sat Oct  1 16:53:45 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pycached's documentation!
====================================


Installing
----------

- ``pip install pycached``
- ``pip install pycached[redis]``


Usage
-----

Using a cache is as simple as

.. code-block:: python

    >>> from pycached import Cache
    >>> cache = Cache()
    >>> cache.set('key', 'value')
    True
    >>> cache.get('key')
    'value'

Here we are using the :ref:`simplememorycache` but you can use any other listed in :ref:`caches`. All caches contain the same minimum interface which consists on the following functions:

- ``add``: Only adds key/value if key does not exist. Otherwise raises ValueError.
- ``get``: Retrieve value identified by key.
- ``set``: Sets key/value.
- ``multi_get``: Retrieves multiple key/values.
- ``multi_set``: Sets multiple key/values.
- ``exists``: Returns True if key exists False otherwise.
- ``increment``: Increment the value stored in the given key.
- ``delete``: Deletes key and returns number of deleted items.
- ``clear``: Clears the items stored.
- ``raw``: Executes the specified command using the underlying client.


You can also setup cache aliases like in Django settings:

.. literalinclude:: ../examples/cached_alias_config.py
  :language: python
  :linenos:
  :emphasize-lines: 6-26


In `examples folder <https://github.com/fanjindong/pycached/tree/master/examples>`_ you can check different use cases:

- `Python object in Redis <https://github.com/fanjindong/pycached/blob/master/examples/python_object.py>`_
- `Custom serializer for compressing data <https://github.com/fanjindong/pycached/blob/master/examples/serializer_class.py>`_
- `TimingPlugin and HitMissRatioPlugin demos <https://github.com/fanjindong/pycached/blob/master/examples/plugins.py>`_
- `Using marshmallow as a serializer <https://github.com/fanjindong/pycached/blob/master/examples/marshmallow_serializer_class.py>`_
- `Using cached decorator <https://github.com/fanjindong/pycached/blob/master/examples/cached_decorator.py>`_.
- `Using multi_cached decorator <https://github.com/fanjindong/pycached/blob/master/examples/multicached_decorator.py>`_.


Contents
--------

.. toctree::

  caches
  serializers
  plugins
  configuration
  decorators
  locking
  testing
  changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
