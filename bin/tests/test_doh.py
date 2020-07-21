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

from bin.resolve_dns import Fetch_DNS

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

    @patch('requests.Session')
    @patch('bin.parse_commands.getArgFromSTDIN')
    def testCommandLine_checkjsondns_configsWithoutCNAME_DnsIndex(self, getArgFromSTDIN, mockSessionObj):

        stdin = []
        stdin.append('["property_1", "dummy1", "www.alquist.nl"]')
        stdin.append('["property_2", "dummy2", "akamai1.alquist.nl,akamai2.alquist.nl"]')

        getArgFromSTDIN.return_value = "\n".join(stdin)

        session = mockSessionObj()
        response = MockResponse()
        response.reset()

        dnsResponses = [
            "{}/json/doh/www.alquist.nl_AAAA.json".format(self.basedir),
            "{}/json/doh/akamai1.alquist.nl_A.json".format(self.basedir),
            "{}/json/doh/akamai2.alquist.nl_A.json".format(self.basedir),  
        ]   

        for mockJson in dnsResponses:
            response.appendResponse(response.getJSONFromFile(mockJson))

        session.get.return_value = response
        response.status_code = 200
        response.headers = {}

        args = [ "checkjsondns", "configsWithoutCNAME", "--dns-index", "2" ]

        commandTester = CommandTester(self)
        stdOutResultArray = commandTester.wrapSuccessCommandStdOutOnly(func=main, args=args)
        
        self.assertEquals( len(stdOutResultArray), 1 )

        row = json.loads(stdOutResultArray[0])
        self.assertEquals( row[0], "property_1" )
        self.assertEquals( row[1], "dummy1" )
        self.assertEquals( row[2], "www.alquist.nl" )

    @patch('requests.Session')
    @patch('bin.parse_commands.getArgFromSTDIN')
    def testCommandLine_checkjsondns_configsWithoutCNAME(self, getArgFromSTDIN, mockSessionObj):

        stdin = []
        stdin.append('["property_1", "www.alquist.nl"]')
        stdin.append('["property_2", "akamai1.alquist.nl,akamai2.alquist.nl"]')

        getArgFromSTDIN.return_value = "\n".join(stdin)

        session = mockSessionObj()
        response = MockResponse()
        response.reset()

        dnsResponses = [
            "{}/json/doh/www.alquist.nl_AAAA.json".format(self.basedir),
            "{}/json/doh/akamai1.alquist.nl_A.json".format(self.basedir),
            "{}/json/doh/akamai2.alquist.nl_A.json".format(self.basedir),  
        ]   

        for mockJson in dnsResponses:
            response.appendResponse(response.getJSONFromFile(mockJson))

        session.get.return_value = response
        response.status_code = 200
        response.headers = {}

        args = [ "checkjsondns", "configsWithoutCNAME" ]

        commandTester = CommandTester(self)
        stdOutResultArray = commandTester.wrapSuccessCommandStdOutOnly(func=main, args=args)
        
        self.assertEquals( len(stdOutResultArray), 1 )

        row = json.loads(stdOutResultArray[0])
        self.assertEquals( row[0], "property_1" )
        self.assertEquals( row[1], "www.alquist.nl" )

    @patch('requests.Session')
    @patch('bin.parse_commands.getArgFromSTDIN')
    def testCommandLine_checkjsondns_configsFullyCNAMED(self, getArgFromSTDIN, mockSessionObj):

        stdin = []
        stdin.append('["property_1", "www.alquist.nl"]')
        stdin.append('["property_2", "akamai1.alquist.nl,akamai2.alquist.nl"]')

        getArgFromSTDIN.return_value = "\n".join(stdin)

        session = mockSessionObj()
        response = MockResponse()
        response.reset()

        dnsResponses = [
            "{}/json/doh/www.alquist.nl_AAAA.json".format(self.basedir),
            "{}/json/doh/akamai1.alquist.nl_A.json".format(self.basedir),
            "{}/json/doh/akamai2.alquist.nl_A.json".format(self.basedir),  
        ]   

        for mockJson in dnsResponses:
            response.appendResponse(response.getJSONFromFile(mockJson))

        session.get.return_value = response
        response.status_code = 200
        response.headers = {}

        args = [ "checkjsondns", "configsFullyCNAMED" ]

        commandTester = CommandTester(self)
        stdOutResultArray = commandTester.wrapSuccessCommandStdOutOnly(func=main, args=args)
        
        self.assertEquals( len(stdOutResultArray), 1 )

        row = json.loads(stdOutResultArray[0])
        self.assertEquals( row[0], "property_2" )
        self.assertEquals( row[1], "akamai1.alquist.nl,akamai2.alquist.nl" )
    

    @patch('requests.Session')
    @patch('bin.parse_commands.getArgFromSTDIN')
    def testCommandLine_checkjsondns_configsWithCNAME(self, getArgFromSTDIN, mockSessionObj):

        stdin = []
        stdin.append('["property_1", "www.alquist.nl"]')
        stdin.append('["property_2", "akamai1.alquist.nl,akamai2.alquist.nl"]')

        getArgFromSTDIN.return_value = "\n".join(stdin)

        session = mockSessionObj()
        response = MockResponse()
        response.reset()

        dnsResponses = [
            "{}/json/doh/www.alquist.nl_AAAA.json".format(self.basedir),
            "{}/json/doh/akamai1.alquist.nl_A.json".format(self.basedir),
            "{}/json/doh/akamai2.alquist.nl_A.json".format(self.basedir),  
        ]   

        for mockJson in dnsResponses:
            response.appendResponse(response.getJSONFromFile(mockJson))

        session.get.return_value = response
        response.status_code = 200
        response.headers = {}

        args = [ "checkjsondns", "configsWithCNAME" ]

        commandTester = CommandTester(self)
        stdOutResultArray = commandTester.wrapSuccessCommandStdOutOnly(func=main, args=args)
        
        self.assertEquals( len(stdOutResultArray), 1 )

        row = json.loads(stdOutResultArray[0])
        self.assertEquals( row[0], "property_2" )
        self.assertEquals( row[1], "akamai1.alquist.nl,akamai2.alquist.nl" )

    @patch('requests.Session')
    @patch('bin.parse_commands.getArgFromSTDIN')
    def testCommandLine_checkjsondns_hostsCNAMED2(self, getArgFromSTDIN, mockSessionObj):

        stdin = []
        stdin.append('["property_1", "www.alquist.nl"]')
        stdin.append('["property_2", "akamai1.alquist.nl,akamai2.alquist.nl"]')

        getArgFromSTDIN.return_value = "\n".join(stdin)

        session = mockSessionObj()
        response = MockResponse()
        response.reset()

        dnsResponses = [
            "{}/json/doh/www.alquist.nl_AAAA.json".format(self.basedir),
            "{}/json/doh/akamai1.alquist.nl_A.json".format(self.basedir),
            "{}/json/doh/akamai2.alquist.nl_A.json".format(self.basedir),  
        ]   

        for mockJson in dnsResponses:
            response.appendResponse(response.getJSONFromFile(mockJson))

        session.get.return_value = response
        response.status_code = 200
        response.headers = {}

        args = [ "checkjsondns", "hostsCNAMED" ]

        commandTester = CommandTester(self)
        stdOutResultArray = commandTester.wrapSuccessCommandStdOutOnly(func=main, args=args)
        
        self.assertEquals( len(stdOutResultArray), 1 )

        row = json.loads(stdOutResultArray[0])
        self.assertEquals( row[0], "property_2" )
        self.assertEquals( row[1], "akamai1.alquist.nl,akamai2.alquist.nl" )

        stdin = []
        stdin.append('["property_3", "www.alquist.nl,akamai1.alquist.nl,akamai2.alquist.nl"]')

        getArgFromSTDIN.return_value = "\n".join(stdin)

        session = mockSessionObj()
        response = MockResponse()
        response.reset()

        dnsResponses = [
            "{}/json/doh/www.alquist.nl_AAAA.json".format(self.basedir),
            "{}/json/doh/akamai1.alquist.nl_A.json".format(self.basedir),
            "{}/json/doh/akamai2.alquist.nl_A.json".format(self.basedir),  
        ]   

        for mockJson in dnsResponses:
            response.appendResponse(response.getJSONFromFile(mockJson))

        session.get.return_value = response
        response.status_code = 200
        response.headers = {}

        args = [ "checkjsondns", "hostsCNAMED" ]

        commandTester = CommandTester(self)
        stdOutResultArray = commandTester.wrapSuccessCommandStdOutOnly(func=main, args=args)
        
        self.assertEquals( len(stdOutResultArray), 1 )

        row = json.loads(stdOutResultArray[0])
        self.assertEquals( row[0], "property_3" )
        self.assertEquals( row[1], "akamai1.alquist.nl,akamai2.alquist.nl" )

    @patch('requests.Session')
    @patch('bin.parse_commands.getArgFromSTDIN')
    def testCommandLine_checkjsondns_hostsNotCNAMED(self, getArgFromSTDIN, mockSessionObj):

        stdin = []
        stdin.append('["property_1", "www.alquist.nl"]')
        stdin.append('["property_2", "akamai1.alquist.nl,akamai2.alquist.nl"]')

        getArgFromSTDIN.return_value = "\n".join(stdin)

        session = mockSessionObj()
        response = MockResponse()
        response.reset()

        dnsResponses = [
            "{}/json/doh/www.alquist.nl_AAAA.json".format(self.basedir),
            "{}/json/doh/akamai1.alquist.nl_A.json".format(self.basedir),
            "{}/json/doh/akamai2.alquist.nl_A.json".format(self.basedir),  
        ]   

        for mockJson in dnsResponses:
            response.appendResponse(response.getJSONFromFile(mockJson))

        session.get.return_value = response
        response.status_code = 200
        response.headers = {}

        args = [ "checkjsondns", "hostsNotCNAMED" ]

        commandTester = CommandTester(self)
        stdOutResultArray = commandTester.wrapSuccessCommandStdOutOnly(func=main, args=args)
        
        self.assertEquals( len(stdOutResultArray), 1 )

        row = json.loads(stdOutResultArray[0])
        self.assertEquals( row[0], "property_1" )
        self.assertEquals( row[1], "www.alquist.nl" )

    @patch('requests.Session')
    @patch('bin.parse_commands.getArgFromSTDIN')
    def testCommandLine_checkjsondns_hostsNotCNAMED(self, getArgFromSTDIN, mockSessionObj):

        stdin = []
        stdin.append('["property_1", "www.alquist.nl,notfound.alquist.nl"]')
        stdin.append('["property_2", "akamai1.alquist.nl,akamai2.alquist.nl,notfound.alquist.nl"]')

        getArgFromSTDIN.return_value = "\n".join(stdin)

        session = mockSessionObj()
        response = MockResponse()
        response.reset()

        dnsResponses = [
            "{}/json/doh/www.alquist.nl_AAAA.json".format(self.basedir),
            "{}/json/doh/notfound.alquist.nl_NXDomain.json".format(self.basedir),
            "{}/json/doh/akamai1.alquist.nl_A.json".format(self.basedir),
            "{}/json/doh/akamai2.alquist.nl_A.json".format(self.basedir),  
            "{}/json/doh/notfound.alquist.nl_NXDomain.json".format(self.basedir)
        ]   

        for mockJson in dnsResponses:
            response.appendResponse(response.getJSONFromFile(mockJson))

        session.get.return_value = response
        response.status_code = 200
        response.headers = {}

        args = [ "checkjsondns", "hostsNotCNAMED" ]

        commandTester = CommandTester(self)
        stdOutResultArray = commandTester.wrapSuccessCommandStdOutOnly(func=main, args=args)
        
        self.assertEquals( len(stdOutResultArray), 2 )

        row = json.loads(stdOutResultArray[0])
        self.assertEquals( row[0], "property_1" )
        self.assertEquals( row[1], "www.alquist.nl,notfound.alquist.nl" )

        row = json.loads(stdOutResultArray[1])
        self.assertEquals( row[0], "property_2" )
        self.assertEquals( row[1], "notfound.alquist.nl" )

    @patch('requests.Session')
    @patch('bin.parse_commands.getArgFromSTDIN')
    def testCommandLine_checkjsondns_hostsCNAMED(self, getArgFromSTDIN, mockSessionObj):

        stdin = []
        stdin.append('["property_1", "www.alquist.nl,notfound.alquist.nl"]')
        stdin.append('["property_2", "akamai1.alquist.nl,akamai2.alquist.nl,notfound.alquist.nl"]')

        getArgFromSTDIN.return_value = "\n".join(stdin)

        session = mockSessionObj()
        response = MockResponse()
        response.reset()

        dnsResponses = [
            "{}/json/doh/www.alquist.nl_AAAA.json".format(self.basedir),
            "{}/json/doh/notfound.alquist.nl_NXDomain.json".format(self.basedir),
            "{}/json/doh/akamai1.alquist.nl_A.json".format(self.basedir),
            "{}/json/doh/akamai2.alquist.nl_A.json".format(self.basedir),  
            "{}/json/doh/notfound.alquist.nl_NXDomain.json".format(self.basedir)
        ]   

        for mockJson in dnsResponses:
            response.appendResponse(response.getJSONFromFile(mockJson))

        session.get.return_value = response
        response.status_code = 200
        response.headers = {}

        args = [ "checkjsondns", "hostsCNAMED" ]

        commandTester = CommandTester(self)
        stdOutResultArray = commandTester.wrapSuccessCommandStdOutOnly(func=main, args=args)
        
        self.assertEquals( len(stdOutResultArray), 1 )

        row = json.loads(stdOutResultArray[0])
        self.assertEquals( row[0], "property_2" )
        self.assertEquals( row[1], "akamai1.alquist.nl,akamai2.alquist.nl" )
        

    @patch('requests.Session')
    @patch('bin.parse_commands.getArgFromSTDIN')
    def testCommandLine_checkdnshostStdIn(self, getArgFromSTDIN, mockSessionObj):

        stdin = []
        stdin.append('www.alquist.nl')
        stdin.append('akamai1.alquist.nl')
        stdin.append('akamai2.alquist.nl')

        getArgFromSTDIN.return_value = "\n".join(stdin)

        session = mockSessionObj()
        response = MockResponse()

        dnsResponses = [
            "{}/json/doh/www.alquist.nl_AAAA.json".format(self.basedir),
            "{}/json/doh/akamai1.alquist.nl_A.json".format(self.basedir),
            "{}/json/doh/akamai2.alquist.nl_A.json".format(self.basedir),
            
            "{}/json/doh/www.alquist.nl_AAAA.json".format(self.basedir),
            "{}/json/doh/akamai1.alquist.nl_A.json".format(self.basedir),
            "{}/json/doh/akamai2.alquist.nl_A.json".format(self.basedir)
            
        ]   

        for mockJson in dnsResponses:
            response.appendResponse(response.getJSONFromFile(mockJson))

        session.get.return_value = response
        response.status_code = 200
        response.headers = {}

        args = [
               "checkdnshost"
        ]

        commandTester = CommandTester(self)
        stdOutResultArray = commandTester.wrapSuccessCommandStdOutOnly(func=main, args=args)
        
        self.assertEquals( len(stdOutResultArray), 4 )      

        row = json.loads(stdOutResultArray[0])
        self.assertEquals( len(row), 3 )
        header = ["isAkamai", "domain", "resolution"]

        self.assertIn(row[0],header)
        self.assertIn(row[1],header)
        self.assertIn(row[2],header)

        row = json.loads(stdOutResultArray[1])
        self.assertFalse(  row[0] )
        self.assertEquals( row[1], "www.alquist.nl" )
        self.assertEquals( row[2], "d2c99t9e0sxfl6.cloudfront.net.,2600:9000:21da:7800:c:1662:4a80:93a1,2600:9000:21da:5800:c:1662:4a80:93a1,2600:9000:21da:9800:c:1662:4a80:93a1,2600:9000:21da:ea00:c:1662:4a80:93a1,2600:9000:21da:6600:c:1662:4a80:93a1,2600:9000:21da:ee00:c:1662:4a80:93a1,2600:9000:21da:4c00:c:1662:4a80:93a1,2600:9000:21da:3e00:c:1662:4a80:93a1" )
        
        row = json.loads(stdOutResultArray[2])
        self.assertTrue(  row[0] )
        self.assertEquals( row[1], "akamai1.alquist.nl" )
        self.assertEquals( row[2], "akamai.alquist.nl.edgekey.net.,e12284.x.akamaiedge.net." )
        
        row = json.loads(stdOutResultArray[3])
        self.assertTrue(  row[0] )
        self.assertEquals( row[1], "akamai2.alquist.nl" )
        self.assertEquals( row[2], "s528007553.sc.qa01en25.com.alquist.nl.,akamai2.cdn.alquist.nl.,akamai.alquist.nl.edgekey.net.,e12284.x.akamaiedge.net." )
          

    @patch('requests.Session')
    def testCommandLine_checkdnshost(self, mockSessionObj):

        session = mockSessionObj()
        response = MockResponse()

        dnsResponses = [
            "{}/json/doh/www.alquist.nl_AAAA.json".format(self.basedir),
            "{}/json/doh/akamai1.alquist.nl_A.json".format(self.basedir),
            "{}/json/doh/akamai2.alquist.nl_A.json".format(self.basedir),
            
            "{}/json/doh/www.alquist.nl_AAAA.json".format(self.basedir),
            "{}/json/doh/akamai1.alquist.nl_A.json".format(self.basedir),
            "{}/json/doh/akamai2.alquist.nl_A.json".format(self.basedir)
            
        ]   

        for mockJson in dnsResponses:
            response.appendResponse(response.getJSONFromFile(mockJson))

        session.get.return_value = response
        response.status_code = 200
        response.headers = {}

        

        args = [
               "checkdnshost",
                "www.alquist.nl",
                "akamai1.alquist.nl",
                "akamai2.alquist.nl"
        ]

        commandTester = CommandTester(self)
        stdOutResultArray = commandTester.wrapSuccessCommandStdOutOnly(func=main, args=args)
        
        self.assertEquals( len(stdOutResultArray), 4 )
        
        row = json.loads(stdOutResultArray[0])
        self.assertEquals( len(row), 3 )
        header = ["isAkamai", "domain", "resolution"]

        self.assertIn(row[0],header)
        self.assertIn(row[1],header)
        self.assertIn(row[2],header)

        row = json.loads(stdOutResultArray[1])
        self.assertFalse(  row[0] )
        self.assertEquals( row[1], "www.alquist.nl" )
        self.assertEquals( row[2], "d2c99t9e0sxfl6.cloudfront.net.,2600:9000:21da:7800:c:1662:4a80:93a1,2600:9000:21da:5800:c:1662:4a80:93a1,2600:9000:21da:9800:c:1662:4a80:93a1,2600:9000:21da:ea00:c:1662:4a80:93a1,2600:9000:21da:6600:c:1662:4a80:93a1,2600:9000:21da:ee00:c:1662:4a80:93a1,2600:9000:21da:4c00:c:1662:4a80:93a1,2600:9000:21da:3e00:c:1662:4a80:93a1" )
        
        row = json.loads(stdOutResultArray[2])
        self.assertTrue(  row[0] )
        self.assertEquals( row[1], "akamai1.alquist.nl" )
        self.assertEquals( row[2], "akamai.alquist.nl.edgekey.net.,e12284.x.akamaiedge.net." )
        
        row = json.loads(stdOutResultArray[3])
        self.assertTrue(  row[0] )
        self.assertEquals( row[1], "akamai2.alquist.nl" )
        self.assertEquals( row[2], "s528007553.sc.qa01en25.com.alquist.nl.,akamai2.cdn.alquist.nl.,akamai.alquist.nl.edgekey.net.,e12284.x.akamaiedge.net." )
        
        args = [
               "checkdnshost",
               "www.alquist.nl,akamai1.alquist.nl,akamai2.alquist.nl"
        ]

        commandTester = CommandTester(self)
        stdOutResultArray = commandTester.wrapSuccessCommandStdOutOnly(func=main, args=args)
        
        self.assertEquals( len(stdOutResultArray), 4 )
        
        row = json.loads(stdOutResultArray[0])
        self.assertEquals( len(row), 3 )
        header = ["isAkamai", "domain", "resolution"]

        self.assertIn(row[0],header)
        self.assertIn(row[1],header)
        self.assertIn(row[2],header)

        row = json.loads(stdOutResultArray[1])
        self.assertFalse(  row[0] )
        self.assertEquals( row[1], "www.alquist.nl" )
        self.assertEquals( row[2], "d2c99t9e0sxfl6.cloudfront.net.,2600:9000:21da:7800:c:1662:4a80:93a1,2600:9000:21da:5800:c:1662:4a80:93a1,2600:9000:21da:9800:c:1662:4a80:93a1,2600:9000:21da:ea00:c:1662:4a80:93a1,2600:9000:21da:6600:c:1662:4a80:93a1,2600:9000:21da:ee00:c:1662:4a80:93a1,2600:9000:21da:4c00:c:1662:4a80:93a1,2600:9000:21da:3e00:c:1662:4a80:93a1" )
        
        row = json.loads(stdOutResultArray[2])
        self.assertTrue(  row[0] )
        self.assertEquals( row[1], "akamai1.alquist.nl" )
        self.assertEquals( row[2], "akamai.alquist.nl.edgekey.net.,e12284.x.akamaiedge.net." )
        
        row = json.loads(stdOutResultArray[3])
        self.assertTrue(  row[0] )
        self.assertEquals( row[1], "akamai2.alquist.nl" )
        self.assertEquals( row[2], "s528007553.sc.qa01en25.com.alquist.nl.,akamai2.cdn.alquist.nl.,akamai.alquist.nl.edgekey.net.,e12284.x.akamaiedge.net." )
        

    @patch('requests.Session')
    def testJsonParseOutputFilter(self, mockSessionObj): 

        session = mockSessionObj()
        response = MockResponse()

        dnsResponses = [
            "{}/json/doh/www.alquist.nl_AAAA.json".format(self.basedir),
            "{}/json/doh/akamai1.alquist.nl_A.json".format(self.basedir),
            "{}/json/doh/akamai3.alquist.nl_A.json".format(self.basedir),
            "{}/json/doh/akamai4.alquist.nl_A.json".format(self.basedir),

            

        ]   

        for mockJson in dnsResponses:
            response.appendResponse(response.getJSONFromFile(mockJson))

        session.get.return_value = response
        response.status_code = 200
        response.headers = {}

        jsonObjArray = list()
       
        jsonObjArray.append(' [["configname_ion3"], ["www.alquist.nl", "akamai1.alquist.nl"]]' )
        jsonObjArray.append(' [["configname_ion4"], ["akamai3.alquist.nl", "akamai4.alquist.nl"]]' )
        fetchDNS = Fetch_DNS()
        returnList = fetchDNS.checkJsonArrayDNS(jsonObjArray, arrayHostIndex=1, returnAkamaiHosts=True)

        self.assertEqual( 2, len(returnList) )
        self.assertEqual("configname_ion3", returnList[0][0][0])
        self.assertEqual("akamai1.alquist.nl", returnList[0][1][0])
        
        self.assertEqual("configname_ion4", returnList[1][0][0])
        self.assertEqual("akamai3.alquist.nl", returnList[1][1][0])
        self.assertEqual("akamai4.alquist.nl", returnList[1][1][1])

    @patch('requests.Session')
    def testJsonParseNestedArrays(self, mockSessionObj): 

        session = mockSessionObj()
        response = MockResponse()

        dnsResponses = [
            "{}/json/doh/www.alquist.nl_AAAA.json".format(self.basedir),
            "{}/json/doh/akamai1.alquist.nl_A.json".format(self.basedir),
            "{}/json/doh/akamai3.alquist.nl_A.json".format(self.basedir),
            "{}/json/doh/akamai4.alquist.nl_A.json".format(self.basedir),

            "{}/json/doh/www.alquist.nl_AAAA.json".format(self.basedir),
            "{}/json/doh/akamai1.alquist.nl_A.json".format(self.basedir),
            "{}/json/doh/akamai3.alquist.nl_A.json".format(self.basedir),
            "{}/json/doh/akamai4.alquist.nl_A.json".format(self.basedir),

        ]   

        for mockJson in dnsResponses:
            response.appendResponse(response.getJSONFromFile(mockJson))

        session.get.return_value = response
        response.status_code = 200
        response.headers = {}

        jsonObjArray = list()
       
        jsonObjArray.append(' [["configname_ion3"], ["www.alquist.nl", "akamai1.alquist.nl"]]' )
        jsonObjArray.append(' [["configname_ion4"], ["akamai3.alquist.nl", "akamai4.alquist.nl"]]' )
        fetchDNS = Fetch_DNS()
        returnList = fetchDNS.checkJsonArrayDNS(jsonObjArray, arrayHostIndex=1)

        self.assertEqual( 2, len(returnList) )
        self.assertEqual("configname_ion3", returnList[0][0][0])
        self.assertEqual("www.alquist.nl", returnList[0][1][0])
        self.assertEqual("akamai1.alquist.nl", returnList[0][1][1])

        self.assertEqual("configname_ion4", returnList[1][0][0])
        self.assertEqual("akamai3.alquist.nl", returnList[1][1][0])
        self.assertEqual("akamai4.alquist.nl", returnList[1][1][1])

    @patch('requests.Session')
    def testJsonParseNestedArrays_AnyAkamai(self, mockSessionObj): 

        session = mockSessionObj()
        response = MockResponse()

        dnsResponses = [
            "{}/json/doh/www.alquist.nl_AAAA.json".format(self.basedir),
            "{}/json/doh/akamai3.alquist.nl_A.json".format(self.basedir),
            "{}/json/doh/akamai4.alquist.nl_A.json".format(self.basedir),

            "{}/json/doh/akamai3.alquist.nl_A.json".format(self.basedir),
            "{}/json/doh/akamai4.alquist.nl_A.json".format(self.basedir)

        ]   

        for mockJson in dnsResponses:
            response.appendResponse(response.getJSONFromFile(mockJson))

        session.get.return_value = response
        response.status_code = 200
        response.headers = {}

        jsonObjArray = list()
       
        fetchDNS = Fetch_DNS()

        jsonObjArray.append(' [["configname_ion3"], ["www.alquist.nl"]]' )
        jsonObjArray.append(' [["configname_ion4"], ["akamai3.alquist.nl", "akamai4.alquist.nl"]]' )
        returnList = fetchDNS.checkJsonArrayDNS(jsonObjArray, arrayHostIndex=1, requireAnyAkamai=True)

        self.assertEqual( 1, len(returnList) )
        self.assertEqual("configname_ion4", returnList[0][0][0])
        self.assertEqual("akamai3.alquist.nl", returnList[0][1][0])
        self.assertEqual("akamai4.alquist.nl", returnList[0][1][1])
    
    @patch('requests.Session')
    def testJsonParseNestedArrays_All_Akamai(self, mockSessionObj): 

        session = mockSessionObj()
        response = MockResponse()

        dnsResponses = [
            "{}/json/doh/www.alquist.nl_AAAA.json".format(self.basedir),
            "{}/json/doh/akamai1.alquist.nl_A.json".format(self.basedir),
            "{}/json/doh/akamai3.alquist.nl_A.json".format(self.basedir),
            "{}/json/doh/akamai4.alquist.nl_A.json".format(self.basedir),

            "{}/json/doh/akamai3.alquist.nl_A.json".format(self.basedir),
            "{}/json/doh/akamai4.alquist.nl_A.json".format(self.basedir)

        ]   

        for mockJson in dnsResponses:
            response.appendResponse(response.getJSONFromFile(mockJson))

        session.get.return_value = response
        response.status_code = 200
        response.headers = {}

        jsonObjArray = list()
       
        jsonObjArray.append(' [["configname_ion3"], ["www.alquist.nl", "akamai1.alquist.nl"] ]' )
        jsonObjArray.append(' [["configname_ion4"], ["akamai3.alquist.nl", "akamai4.alquist.nl"]]' )

        fetchDNS = Fetch_DNS()
        returnList = fetchDNS.checkJsonArrayDNS(jsonObjArray, arrayHostIndex=1, requireAllAkamai=True)

        self.assertEqual( 1, len(returnList) )
        self.assertEqual("configname_ion4", returnList[0][0][0])
        self.assertEqual("akamai3.alquist.nl", returnList[0][1][0])
        self.assertEqual("akamai4.alquist.nl", returnList[0][1][1])

    @patch('requests.Session')
    def testJsonParseArray(self, mockSessionObj):

        session = mockSessionObj()
        response = MockResponse()

        dnsResponses = [
            "{}/json/doh/www.alquist.nl_AAAA.json".format(self.basedir),
            "{}/json/doh/akamai1.alquist.nl_A.json".format(self.basedir),
            "{}/json/doh/akamai2.alquist.nl_A.json".format(self.basedir),
            "{}/json/doh/akamai3.alquist.nl_A.json".format(self.basedir),

            "{}/json/doh/www.alquist.nl_AAAA.json".format(self.basedir),
            "{}/json/doh/akamai1.alquist.nl_A.json".format(self.basedir),
            "{}/json/doh/akamai2.alquist.nl_A.json".format(self.basedir),
            "{}/json/doh/akamai3.alquist.nl_A.json".format(self.basedir)
        ]   

        for mockJson in dnsResponses:
            response.appendResponse(response.getJSONFromFile(mockJson))

        session.get.return_value = response
        response.status_code = 200
        response.headers = {}

        jsonObjArray = list()
        jsonObjArray.append('["configname_ion1", "www.alquist.nl,akamai1.alquist.nl"]' )
        jsonObjArray.append('["configname_ion2", "akamai2.alquist.nl,akamai3.alquist.nl"]' )

        fetchDNS = Fetch_DNS()
        returnList = fetchDNS.checkJsonArrayDNS(jsonObjArray, arrayHostIndex=1)

        self.assertEqual( 2, len(returnList) )

        self.assertEqual("configname_ion1", returnList[0][0])
        self.assertEqual("www.alquist.nl", returnList[0][1].split(",")[0])
        self.assertEqual("akamai1.alquist.nl", returnList[0][1].split(",")[1])

        self.assertEqual("configname_ion2", returnList[1][0].split(",")[0])
        self.assertEqual("akamai2.alquist.nl", returnList[1][1].split(",")[0])
        self.assertEqual("akamai3.alquist.nl", returnList[1][1].split(",")[1])        


    def testLookup(self):
        fetchDNS = Fetch_DNS()
        valueCNAME = fetchDNS.lookupCode(5)
        self.assertEqual("CNAME", valueCNAME)

    @patch('requests.Session')
    def test_MockDNSResponse(self, mockSessionObj):
        session = mockSessionObj()
        response = MockResponse()

        dnsResponses = [
            "{}/json/doh/www.alquist.nl_A.json".format(self.basedir),
            "{}/json/doh/www.akamai.com_AAAA.json".format(self.basedir)
        ]   

        for mockJson in dnsResponses:
            response.appendResponse(response.getJSONFromFile(mockJson))

        session.get.return_value = response
        response.status_code = 200
        response.headers = {}
        
        fetchDNS = Fetch_DNS()
        result = fetchDNS.checkDNSMetadata(["www.alquist.nl", "www.akamai.com" ])
        
        self.assertTrue(result["anyAkamai"])
        self.assertFalse(result["allAkamai"])
        self.assertFalse(result["allIPv6"])
        self.assertTrue(result["anyIPv6"])
        self.assertFalse(result["anyNXDomain"])

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
        

    @patch('requests.Session')
    def test_MockDNSResponse(self, mockSessionObj):
        session = mockSessionObj()
        response = MockResponse()

        dnsResponses = [
            "{}/json/doh/notfound.alquist.nl_NXDomain.json".format(self.basedir)
            
        ]   

        for mockJson in dnsResponses:
            response.appendResponse(response.getJSONFromFile(mockJson))

        session.get.return_value = response
        response.status_code = 200
        response.headers = {}
        
        fetchDNS = Fetch_DNS()
        result = fetchDNS.checkDNSMetadata(["notfound.alquist.nl"])
        
        self.assertFalse(result["anyAkamai"])
        self.assertFalse(result["allAkamai"])
        self.assertFalse(result["allIPv6"])
        self.assertFalse(result["anyIPv6"])
        self.assertTrue(result["anyNXDomain"])
        
    

        


