from pathlib import Path
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
PACKAGE_PARENT = '..'
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from bin.decorator import count_calls
from bin.decorator import cache
from bin.decorator import CacheManager


home = str(Path.home())

cachedir = "{}/Desktop/cache_dir/{}".format(home, "test2")

@count_calls
@cache
def fibonacci(num, test=123):
    if num < 2:
        return num
    return fibonacci(num - 1) + fibonacci(num - 2)

@count_calls
@cache(tempCache=False, directory=cachedir)
def test2(num, test=123):
    if num < 2:
        return num
    return test2(num - 1) + test2(num - 2)

@count_calls
@cache(tempCache=False)
def test3(num, test=123):
    if num < 2:
        return num
    return test3(num - 1) + test3(num - 2)



print( list( CacheManager().get()) )

val=test3(7,33)
print(val)


print( list( CacheManager().get()) )
CacheManager().clear()
print( list( CacheManager().get()) )
pass