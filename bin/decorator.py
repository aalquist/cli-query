import functools
import sys
from functools import partial
from diskcache import Cache

def singleton(cls):
    """Make a class a Singleton class (only one instance)"""
    @functools.wraps(cls)
    def wrapper_singleton(*args, **kwargs):
        if not wrapper_singleton.instance:
            wrapper_singleton.instance = cls(*args, **kwargs)
        return wrapper_singleton.instance
    wrapper_singleton.instance = None
    return wrapper_singleton

@singleton
class CacheManager:
    def __init__(self):
        self.cache = dict()
    
    def get(self):
        return self.cache
    
    def add(self, key, cacheObj):
        self.cache[key] = cacheObj

    def clear(self):
        for i in list(self.cache.values()):
            i.clear()

@singleton
class CallCount:
    def __init__(self):
        self.cache = dict()
    
    def get(self, key):

        if key in self.cache.keys(): 
            num = self.cache[key]
            return num
        else:

            return 0
    
    def clear(self, key):


        if key in self.cache.keys(): 
            del self.cache[key] 
        
    def addToKey(self, key):

        if key in self.cache.keys(): 
            num = self.cache[key]
            self.cache[key] = num + 1
        else:
            self.cache[key] = 1
        
    
def count_calls(func=None, printOut=False):
    """simple function call counter"""

    if func is None:
        return partial(cache)

    @functools.wraps(func)
    def wrapper_count_calls(*args, **kwargs):
        wrapper_count_calls.num_calls += 1
        
        count=CallCount()
        count.addToKey(func.__name__)

        if printOut:
            print(f"Call {wrapper_count_calls.num_calls} of {func.__name__!r}", file=sys.stderr)

        return func(*args, **kwargs)
    wrapper_count_calls.num_calls = 0
    return wrapper_count_calls

def cache(func=None, *, tempCache=True, directory=None):
    """Keep a cache of previous function calls"""

    #Just in case func is null, call the same without func=None
    if func is None:
        return partial(cache, tempCache=tempCache)

    @functools.wraps(func)
    def wrapper_cache(*args, **kwargs):
        cache_key = args + tuple(kwargs.items())
        if cache_key not in wrapper_cache.cache:
            wrapper_cache.cache[cache_key] = func(*args, **kwargs)
        return wrapper_cache.cache[cache_key]
    
    if(tempCache):
        wrapper_cache.cache = Cache()
    else:

        if directory is None:
            directory = "cache/{}".format(func.__name__)

        wrapper_cache.cache = Cache(directory=directory)

    cacheManager = CacheManager()
    cacheManager.add(wrapper_cache.cache.directory, wrapper_cache.cache)

    return wrapper_cache

