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

from bin.resolve_dns import checkDNSMetadata, lookupCode, checkJsonArrayDNS

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

    def testJsonParseOutputFilter(self): 
        jsonObjArray = list()
       
        jsonObjArray.append(' [["configname_ion3"], ["www.alquist.nl", "akamai1.alquist.nl"]]' )
        jsonObjArray.append(' [["configname_ion4"], ["akamai3.alquist.nl", "akamai4.alquist.nl"]]' )
        returnList = checkJsonArrayDNS(jsonObjArray, arrayHostIndex=1, returnAkamaiHosts=True)

        self.assertEqual( 2, len(returnList) )
        self.assertEqual("configname_ion3", returnList[0][0][0])
        self.assertEqual("akamai1.alquist.nl", returnList[0][1][0])
        
        self.assertEqual("configname_ion4", returnList[1][0][0])
        self.assertEqual("akamai3.alquist.nl", returnList[1][1][0])
        self.assertEqual("akamai4.alquist.nl", returnList[1][1][1])

    def testJsonParseNestedArrays(self): 
        jsonObjArray = list()
       
        jsonObjArray.append(' [["configname_ion3"], ["www.alquist.nl", "akamai1.alquist.nl"]]' )
        jsonObjArray.append(' [["configname_ion4"], ["akamai3.alquist.nl", "akamai4.alquist.nl"]]' )
        returnList = checkJsonArrayDNS(jsonObjArray, arrayHostIndex=1)

        self.assertEqual( 2, len(returnList) )
        self.assertEqual("configname_ion3", returnList[0][0][0])
        self.assertEqual("www.alquist.nl", returnList[0][1][0])
        self.assertEqual("akamai1.alquist.nl", returnList[0][1][1])

        self.assertEqual("configname_ion4", returnList[1][0][0])
        self.assertEqual("akamai3.alquist.nl", returnList[1][1][0])
        self.assertEqual("akamai4.alquist.nl", returnList[1][1][1])

    def testJsonParseNestedArrays_AnyAkamai(self): 
        jsonObjArray = list()
       
        jsonObjArray.append(' [["configname_ion3"], ["www.alquist.nl"]]' )
        jsonObjArray.append(' [["configname_ion4"], ["akamai3.alquist.nl", "akamai4.alquist.nl"]]' )
        returnList = checkJsonArrayDNS(jsonObjArray, arrayHostIndex=1, requireAnyAkamai=True)

        self.assertEqual( 1, len(returnList) )
        self.assertEqual("configname_ion4", returnList[0][0][0])
        self.assertEqual("akamai3.alquist.nl", returnList[0][1][0])
        self.assertEqual("akamai4.alquist.nl", returnList[0][1][1])
    
    def testJsonParseNestedArrays_All_Akamai(self): 
        jsonObjArray = list()
       
        jsonObjArray.append(' [["configname_ion3"], ["www.alquist.nl", "akamai1.alquist.nl"] ]' )
        jsonObjArray.append(' [["configname_ion4"], ["akamai3.alquist.nl", "akamai4.alquist.nl"]]' )
        returnList = checkJsonArrayDNS(jsonObjArray, arrayHostIndex=1, requireAllAkamai=True)

        self.assertEqual( 1, len(returnList) )
        self.assertEqual("configname_ion4", returnList[0][0][0])
        self.assertEqual("akamai3.alquist.nl", returnList[0][1][0])
        self.assertEqual("akamai4.alquist.nl", returnList[0][1][1])

    def testJsonParseArray(self):

        jsonObjArray = list()
        jsonObjArray.append('["configname_ion1", "www.alquist.nl,akamai1.alquist.nl"]' )
        jsonObjArray.append('["configname_ion2", "akamai2.alquist.nl,akamai3.alquist.nl"]' )
        returnList = checkJsonArrayDNS(jsonObjArray, arrayHostIndex=1)

        self.assertEqual( 2, len(returnList) )

        self.assertEqual("configname_ion1", returnList[0][0])
        self.assertEqual("www.alquist.nl", returnList[0][1].split(",")[0])
        self.assertEqual("akamai1.alquist.nl", returnList[0][1].split(",")[1])

        self.assertEqual("configname_ion2", returnList[1][0].split(",")[0])
        self.assertEqual("akamai2.alquist.nl", returnList[1][1].split(",")[0])
        self.assertEqual("akamai3.alquist.nl", returnList[1][1].split(",")[1])        


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
        

        

        


