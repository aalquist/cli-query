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
import json
import sys
import json


from unittest.mock import patch
from akamai.edgegrid import EdgeGridAuth, EdgeRc

from bin.parse_commands import main 
from bin.tests.unittest_utils import CommandTester, MockResponse

from bin.resolve_dns import checkDNSMetadata

from bin.send_analytics import Analytics 


class Doh_Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        obj = Analytics()
        obj.disableAnalytics()

    @classmethod
    def tearDownClass(cls):
        obj = Analytics()
        obj.enableAnalytics()

    def setUp(self):
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        self.dnsQueries = [
            "{}/json/doh/www.alquist.nl_A.json".format(self.basedir),
            "{}/json/doh/www.akamai.com_AAAA.json".format(self.basedir)
        ]
    

    @patch('requests.Session')
    def test_MockDNSResponse(self, mockSessionObj):
        session = mockSessionObj()
        response = MockResponse()

        for mockJson in self.dnsQueries:
            response.appendResponse(response.getJSONFromFile(mockJson))
            
        
        session.get.return_value = response
        response.status_code = 200
        response.headers = {}
        
        result = checkDNSMetadata(["www.alquist.nl", "www.akamai.com" ])
        
        self.assertFalse(result["anyAkamai"])
        self.assertFalse(result["allAkamai"])
        self.assertFalse(result["allIPv6"])
        self.assertTrue(result["anyIPv6"])


        


