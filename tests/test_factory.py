from pycached.factory import caches
from pycached.serializers import JsonSerializer

caches.set_config({
    'default': {
        'cache': "pycached.SimpleMemoryCache",
        'serializer': {
            'class': "pycached.serializers.JsonSerializer"
        },
        'namespace': 'cache'
    },
    'redis_alt': {
        'cache': "pycached.RedisCache",
        'endpoint': "192.168.3.3",
        'db': 0,
        'serializer': {
            'class': JsonSerializer
        },
        'namespace': 'cache'
    }
})

def test_caches():
    cache = caches.get('redis_alt')
    cache.set('test', 'c')
    assert cache.get('test') == 'c'