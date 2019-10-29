# Copyright 2017 Akamai Technologies, Inc. All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

import os
import datetime

from bin.decorator import count_calls
from bin.decorator import cacheFunctionCall

from bin.decorator import cache
from diskcache import Cache
from bin.decorator import CacheManager
from bin.decorator import CallCount

from bin.credentialfactory import CredentialFactory

from bin.fetch import CachedContextHandler

from bin.tests.unittest_utils import MockResponse

from unittest.mock import patch

import json


class CachingTest(unittest.TestCase):

    def setUp(self):
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        self.edgerc = "{}/other/.dummy_edgerc".format(self.basedir)
        
    @patch('requests.Session')
    def test_CachedContextHandler(self, mockSessionObj):

        factory = CredentialFactory()
        self.context = factory.load(self.edgerc, None, "account_key_789")

        cache = Cache()
        cachedHandler = CachedContextHandler(self.context, cache)

        session = mockSessionObj()
        response = MockResponse()

        session.get.return_value = response
        response.status_code = 200

        datevalue = str( datetime.datetime.now() )

        response.appendResponse(json.dumps( { "date" : datevalue } ))


        url = "https://test"
        _, value = cachedHandler.get(url, requestHeaders=None, bypassCache=False)

        newDict = json.loads(value)
        newDate = newDict["date"]

        self.assertEquals(datevalue, newDate)

        response.appendResponse(json.dumps( { "date" : "date-should-not-be-used" } ))

        url = "https://test"
        _, value = cachedHandler.get(url, requestHeaders=None, bypassCache=False)

        newDict = json.loads(value)
        newDate = newDict["date"]

        self.assertEquals(datevalue, newDate)
        response.reset()

        response.appendResponse(json.dumps( { "date" : "date-should-be-used" } ))
        response.status_code = 200
        
        url = "https://test"
        _, value = cachedHandler.get(url, requestHeaders=None, bypassCache=True)

        newDict = json.loads(value)
        newDate = newDict["date"]

        self.assertEquals("date-should-be-used", newDate)


        
    def test_caching_function_helper(self):

        def oneFunc(one, two, three):
            return "one func " + str(one) + " " + str(two) + " " + str(three)

        def oneFuncShouldbeCached(one, two, three):
            return "something wrong"

        def functionError(one, two, three, four):
            raise EnvironmentError()

        cache = dict()
        val = cacheFunctionCall(oneFunc, cache, 1,2,3)
        self.assertEqual("one func 1 2 3", val )

        val = cacheFunctionCall(oneFuncShouldbeCached, cache, 1,2,3)
        self.assertEqual("one func 1 2 3", val )

        with self.assertRaises(EnvironmentError):
            cacheFunctionCall(functionError, cache, 1,2,3,4)

        self.assertEqual(1, len(cache) )
        

    def test_caching_decorators(self):
        
        @count_calls
        @cache
        def fibonacci(num):
            if num < 2:
                return num
            return fibonacci(num - 1) + fibonacci(num - 2)
        
        f1 = fibonacci(7)
        
        self.assertEqual(13, CallCount().get("fibonacci"))

        CallCount().clear("fibonacci")
        self.assertEqual(0, CallCount().get("fibonacci"))

        f2 = fibonacci(7)
        self.assertEqual(f1, f2)

        self.assertEqual(1, CallCount().get("fibonacci"))
        

    

if __name__ == '__main__':
    unittest.main()