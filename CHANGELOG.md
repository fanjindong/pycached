# CHANGELOG

## 0.10.1 (2018-11-15)

* Cancel the previous ttl timer if exists when setting a new value in the in-memory cache [#424](https://github.com/argaen/pycached/issues/424) - Minh Tu Le

* Add python 3.7 to CI, now its supported! [#420](https://github.com/argaen/pycached/issues/420) - Manuel Miranda

* Add function as parameter for key_builder [#417](https://github.com/argaen/pycached/issues/417) - Manuel Miranda

* Always use __name__ when getting logger [#412](https://github.com/argaen/pycached/issues/412) - Mansur Mamkin

* Format code with black [#410](https://github.com/argaen/pycached/issues/410) - Manuel Miranda


## 0.10.0 (2018-06-17)

* Cache can be disabled in decorated functions using `cache_read` and `cache_write` [#404](https://github.com/argaen/pycached/issues/404) - Josep Cugat

* Cache constructor can receive now default ttl [#405](https://github.com/argaen/pycached/issues/405) - Josep Cugat
## 0.9.1 (2018-04-27)

* Single deploy step [#395](https://github.com/argaen/pycached/issues/395) - Manuel Miranda

* Catch ImportError when importing optional msgpack [#398](https://github.com/argaen/pycached/issues/398) - Paweł Kowalski

* Lazy load redis asyncio.Lock [#397](https://github.com/argaen/pycached/issues/397) - Jordi Soucheiron



## 0.9.0 (2018-04-24)

* Bug #389/propagate redlock exceptions [#394](https://github.com/argaen/pycached/issues/394) - Manuel Miranda
  ___aexit__ was returning whether asyncio Event was removed or not. In
some cases this was avoiding the context manager to propagate
exceptions happening inside. Now its not returning anything and will
raise always any exception raised from inside_

* Fix sphinx build [#392](https://github.com/argaen/pycached/issues/392) - Manuel Miranda
  _Also add extra step in build pipeline to avoid future errors._

* Update alias config when config already exists [#383](https://github.com/argaen/pycached/issues/383) - Josep Cugat

* Ensure serializers are instances [#379](https://github.com/argaen/pycached/issues/379) - Manuel Miranda

* Add MsgPackSerializer [#370](https://github.com/argaen/pycached/issues/370) - Adam Hopkins

* Add create_connection_timeout for redis>=1.0.0 when creating connections [#368](https://github.com/argaen/pycached/issues/368) - tmarques82

* Fixed spelling error in serializers.py [#371](https://github.com/argaen/pycached/issues/371) - Jared Shields
## 0.8.0 (2017-11-08)


* Add pypy support in build pipeline [#359](https://github.com/argaen/pycached/issues/359) - Manuel Miranda

* Fix multicached bug when using keys as an arg rather than kwarg [#356](https://github.com/argaen/pycached/issues/356) - Manuel Miranda

* Reuse cache when using decorators with alias [#355](https://github.com/argaen/pycached/issues/355) - Manuel Miranda

* Cache available from function.cache object for decorated functions [#354](https://github.com/argaen/pycached/issues/354) - Manuel Miranda

* aioredis and aiomcache are now optional dependencies [#337](https://github.com/argaen/pycached/issues/337) - Jair Henrique

* Generate wheel package on release [#338](https://github.com/argaen/pycached/issues/338) - Jair Henrique

* Add key_builder param to caches to customize keys [#315](https://github.com/argaen/pycached/issues/315) - Manuel Miranda


## 0.7.2 (2017-07-23)

#### Other

* Add key_builder param to caches to customize keys [#310](https://github.com/argaen/pycached/issues/310) - Manuel Miranda

* Propagate correct message on memcached connector error [#309](https://github.com/argaen/pycached/issues/309) - Manuel Miranda



## 0.7.1 (2017-07-15)


* Remove explicit loop usages [#305](https://github.com/argaen/pycached/issues/305) - Manuel Miranda

* Remove bad logging configuration [#304](https://github.com/argaen/pycached/issues/304) - Manuel Miranda


## 0.7.0 (2017-07-01)

* Upgrade to aioredis 0.3.3. - Manuel Miranda

* Get CMD now returns values that evaluate to False correctly [#282](https://github.com/argaen/pycached/issues/282) - Manuel Miranda

* New locks public API exposed [#279](https://github.com/argaen/pycached/issues/279) - Manuel Miranda
  _Users can now use pycached.lock.RedLock and
pycached.lock.OptimisticLock_

* Memory now uses new NullSerializer [#273](https://github.com/argaen/pycached/issues/273) - Manuel Miranda
  _Memory is a special case and doesn't need a serializer  because
anything can be stored in memory. Created a new  NullSerializer that
does nothing which is the default  that SimpleMemoryCache will use
now._

* Multi_cached can use args for key_from_attr [#271](https://github.com/argaen/pycached/issues/271) - Manuel Miranda
  _before only params defined in kwargs where working due to the
behavior defined in _get_args_dict function. This has now been  fixed
and it behaves as expected._

* Removed cached key_from_attr [#274](https://github.com/argaen/pycached/issues/274) - Manuel Miranda
  _To reproduce the same behavior, use the new `key_builder` attr_

* Removed settings module. - Manuel Miranda

## 0.6.1 (2017-06-12)

#### Other

* Removed connection reusage for decorators [#267](https://github.com/argaen/pycached/issues/267)- Manuel Miranda (thanks @dmzkrsk)
  _when decorated function is costly connections where being kept while
being iddle. This is a bad scenario and this reverts back to using a
connection from the cache pool for every cache operation_

* Key_builder for cached [#265](https://github.com/argaen/pycached/issues/265) - Manuel Miranda
  _Also fixed a bug with multi_cached where key_builder wasn't  applied
when saving the keys_

* Updated aioredis (0.3.1) and aiomcache (0.5.2) versions - Manuel Miranda



## 0.6.0 (2017-06-05)

#### New

* Cached supports stampede locking [#249](https://github.com/argaen/pycached/issues/249) - Manuel Miranda

* Memory redlock implementation [#241](https://github.com/argaen/pycached/issues/241) - Manuel Miranda

* Memcached redlock implementation [#240](https://github.com/argaen/pycached/issues/240) - Manuel Miranda

* Redis redlock implementation [#235](https://github.com/argaen/pycached/issues/235) - Manuel Miranda

* Add close function to clean up resources [#236](https://github.com/argaen/pycached/issues/236) - Quinn Perfetto

  _Call `cache.close()` to close a pool and its connections_

* `caches.create` works without alias [#253](https://github.com/argaen/pycached/issues/253) - Manuel Miranda


#### Changes

* Decorators use JsonSerializer by default now [#258](https://github.com/argaen/pycached/issues/258) - Manuel Miranda

  _Also renamed DefaultSerializer to StringSerializer_

* Decorators use single connection [#257](https://github.com/argaen/pycached/issues/257) - Manuel Miranda

  _Decorators (except cached_stampede) now use a single connection for
each function call. This means connection doesn't go back to the pool
after each cache call. Since the cache instance is the same for a
decorated function, this means that the pool size must be high if
there is big expected concurrency for that given function_

* Change close to clear for redis [#239](https://github.com/argaen/pycached/issues/239) - Manuel Miranda

  _clear will free connections but will allow the user to still use the
cache if needed (same behavior for  aiomcache and ofc memory)_


## 0.5.2

* Reuse connection context manager [#225](https://github.com/argaen/pycached/issues/225) [argaen]
* Add performance footprint tests [#228](https://github.com/argaen/pycached/issues/228) [argaen]
* Timeout=0 takes precedence over self.timeout [#227](https://github.com/argaen/pycached/issues/227) [argaen]
* Lock when acquiring redis connection [#224](https://github.com/argaen/pycached/issues/224) [argaen]
* Added performance concurrency tests [#216](https://github.com/argaen/pycached/issues/216) [argaen]


## 0.5.1

* Deprecate settings module [#215](https://github.com/argaen/pycached/issues/215) [argaen]
* Decorators support introspection [#213](https://github.com/argaen/pycached/issues/213) [argaen]


## 0.5.0 (2017-04-29)

* Removed pool reusage for redis. A new one
  is created for each instance [argaen]
* Soft dependencies for redis and memcached [#197](https://github.com/argaen/pycached/issues/197) [argaen]
* Added incr CMD [#188](https://github.com/argaen/pycached/issues/188>) [Manuel
  Miranda]
* Create factory accepts cache args [#209](https://github.com/argaen/pycached/issues/209) [argaen]
* Cached and multi_cached can use alias caches (creates new instance per call) [#205](https://github.com/argaen/pycached/issues/205) [argaen]
* Method ``create`` to create new instances from alias [#204](https://github.com/argaen/pycached/issues/204) [argaen]
* Remove unnecessary warning [#200](https://github.com/argaen/pycached/issues/200) [Petr Timofeev]
* Add asyncio trove classifier [#199](https://github.com/argaen/pycached/issues/199) [Thanos Lefteris]
* Pass pool_size to the underlayed aiomcache [#189](https://github.com/argaen/pycached/issues/189) [Aurélien Busi]
* Added marshmallow example [#181](https://github.com/argaen/pycached/issues/181) [argaen]
* Added example for compression serializer [#179](https://github.com/argaen/pycached/issues/179) [argaen]
* Added BasePlugin.add_hook helper [#173](https://github.com/argaen/pycached/issues/173) [argaen]

#### Breaking

* Refactored how settings and defaults work. Now
  aliases are the only way. [#193](https://github.com/argaen/pycached/issues/193) [argaen]
* Consistency between backends and serializers. With
  SimpleMemoryCache, some data will change on how its stored
  when using DefaultSerializer [#191](https://github.com/argaen/pycached/issues/191) [argaen]


## 0.3.3 (2017-04-06)

* Added CHANGELOG and release process [#172](https://github.com/argaen/pycached/issues/172) [argaen]
* Added pool_min_size pool_max_size to redisbackend [#167](https://github.com/argaen/pycached/issues/167) [argaen]
* Timeout per function. Propagate it correctly with defaults. [#166](https://github.com/argaen/pycached/issues/166) [argaen]
* Added noself arg to cached decorator [#137](https://github.com/argaen/pycached/issues/137) [argaen]
* Cache instance in decorators is built in every call [#135](https://github.com/argaen/pycached/issues/135) [argaen]


## 0.3.1 (2017-02-13)

* Changed add redis to use set with not existing flag [#119](https://github.com/argaen/pycached/issues/119) [argaen]
* Memcached multi_set with ensure_future [#114](https://github.com/argaen/pycached/issues/114) [argaen]


## 0.3.0 (2017-01-12)

* Fixed asynctest issues for timeout tests [#109](https://github.com/argaen/pycached/issues/109) [argaen]
* Created new API class [#108](https://github.com/argaen/pycached/issues/108)
  [argaen]
* Set multicached keys only when non existing [#98](https://github.com/argaen/pycached/issues/98) [argaen]
* Added expire command [#97](https://github.com/argaen/pycached/issues/97) [argaen]
* Ttl tasks are cancelled for memory backend if key is deleted [#92](https://github.com/argaen/pycached/issues/92) [argaen]
* Ignore caching if AIOCACHE_DISABLED is set to 1 [#90](https://github.com/argaen/pycached/issues/90) [argaen]
