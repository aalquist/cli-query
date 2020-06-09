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

from bin.resolve_dns import checkDNSMetadata, lookupCode

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
    
    def testLookup(self):
        valueCNAME = lookupCode(5)
        self.assertEqual("CNAME", valueCNAME)

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
        
        self.assertTrue(result["anyAkamai"])
        self.assertFalse(result["allAkamai"])
        self.assertFalse(result["allIPv6"])
        self.assertTrue(result["anyIPv6"])

        self.assertEqual("www.alquist.nl", result["resolution"][0]["domain"])
        self.assertEqual("CNAME", result["resolution"][0]["dnsJson"]["Answer"][0]["typeName"])
        self.assertEqual("A", result["resolution"][0]["dnsJson"]["Answer"][1]["typeName"])
        
        self.assertEqual("www.akamai.com", result["resolution"][1]["domain"])
        self.assertEqual("CNAME", result["resolution"][1]["dnsJson"]["Answer"][0]["typeName"])
        self.assertEqual("CNAME", result["resolution"][1]["dnsJson"]["Answer"][1]["typeName"])
        self.assertEqual("CNAME", result["resolution"][1]["dnsJson"]["Answer"][2]["typeName"])
        self.assertEqual("AAAA", result["resolution"][1]["dnsJson"]["Answer"][3]["typeName"])
        
        self.assertEqual(False, result["resolution"][0]["isAkamai"])
        self.assertEqual(True, result["resolution"][1]["isAkamai"])

        self.assertEqual(False, result["resolution"][0]["isIPV6"])
        self.assertEqual(True, result["resolution"][1]["isIPV6"])
        

        

        


