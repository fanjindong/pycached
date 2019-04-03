..  _decorators:

Decorators
==========

pycached comes with a couple of decorators for caching results from asynchronous functions. Do not use the decorator in synchronous functions, it may lead to unexpected behavior.

..  _cached:

cached
------

.. automodule:: pycached
  :members: cached

.. literalinclude:: ../examples/cached_decorator.py
  :language: python
  :linenos:

..  _multi_cached:

multi_cached
------------

.. automodule:: pycached
  :members: multi_cached

.. literalinclude:: ../examples/multicached_decorator.py
  :language: python
  :linenos:
