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
from io import StringIO
from collections import OrderedDict

from bin.query_result import QueryResult
from bin.fetch_propertymanager import PropertyManagerFetch
from bin.parse_commands import main 

from unittest.mock import patch
from akamai.edgegrid import EdgeGridAuth, EdgeRc
from bin.credentialfactory import CredentialFactory

from bin.tests.unittest_utils import CommandTester, MockResponse

from bin.parse_commands import main 





class PropertyManagerBulkSearch_Test(unittest.TestCase):

    def setUp(self):
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        self.edgerc = "{}/other/.dummy_edgerc".format(self.basedir)
        self.allsearchresponses = [
            "{}/json/papi/_v1_bulk/rules-search-requests-synch.json".format(self.basedir),
            "{}/json/papi/v1/properties/prp_3/versions/10/rules.json".format(self.basedir),
            "{}/json/papi/v1/properties/prp_1/versions/1/rules.json".format(self.basedir),
            "{}/json/papi/v1/properties/prp_15/versions/2/rules.json".format(self.basedir)
            
        ]

        self.asyncAllsearchresponses = [
            "{}/json/papi/_v1_bulk/rules-search-requests-pending.json".format(self.basedir),
            "{}/json/papi/_v1_bulk/rules-search-requests-pending.json".format(self.basedir),
            "{}/json/papi/_v1_bulk/rules-search-requests-synch.json".format(self.basedir),
            "{}/json/papi/v1/properties/prp_3/versions/10/rules.json".format(self.basedir),
            "{}/json/papi/v1/properties/prp_1/versions/1/rules.json".format(self.basedir),
            "{}/json/papi/v1/properties/prp_15/versions/2/rules.json".format(self.basedir)
            
        ]

        self.allstagingresponses = [
            "{}/json/papi/_v1_bulk/rules-search-requests-synch.json".format(self.basedir),
            "{}/json/papi/v1/properties/prp_1/versions/1/rules.json".format(self.basedir)
            
        ]

        self.asyncAllstagingresponses = [
            "{}/json/papi/_v1_bulk/rules-search-requests-pending.json".format(self.basedir),
            "{}/json/papi/_v1_bulk/rules-search-requests-pending.json".format(self.basedir),
            "{}/json/papi/_v1_bulk/rules-search-requests-synch.json".format(self.basedir),
            "{}/json/papi/v1/properties/prp_1/versions/1/rules.json".format(self.basedir)
            
        ]

        self.asyncAllstagingresponseMaps = [
            { "uri" : "{}/json/papi/_v1_bulk/rules-search-requests-pending.json".format(self.basedir), "code" : 202 },
            { "uri" : "{}/json/papi/_v1_bulk/rules-search-requests-pending.json".format(self.basedir), "code" : 202 },
            { "uri" : "{}/json/papi/_v1_bulk/rules-search-requests-synch.json".format(self.basedir), "code" : 202 },
            { "uri" : "{}/json/papi/v1/properties/prp_1/versions/1/rules.json".format(self.basedir), "code" : 200 },
            { "uri" : "{}/json/papi/v1/properties/prp_1/versions/1/hostnames.json".format(self.basedir), "code" : 200 }            
        ]

        

    def testURLStructure(self):


        factory = CredentialFactory()
        context = factory.load(self.edgerc, None, "account_key_789")

        fetch = PropertyManagerFetch()
        
        url = fetch.buildBulkSearchUrl(context)
        self.assertIn("?accountSwitchKey=account_key_789", url)
        self.assertNotIn("group", url)
        self.assertNotIn("contract", url)

        url = fetch.buildBulkSearchUrl(context,contractId="contract_123")
        self.assertIn("contract_123", url)

        url = fetch.buildBulkSearchUrl(context)
        self.assertNotIn("contract_123", url)

        url = fetch.buildBulkSearchUrl(context,groupId="groupId_123")
        self.assertIn("groupId_123", url)

    @patch('requests.Session')
    def testAsyncIntegration(self, mockSessionObj):
        fetch = PropertyManagerFetch(tempCache=True)

        accountKey="1-abcdef"
        
        contractId="ctr_C-0000"
        

        postdata = {
                        "bulkSearchQuery": {
                            "syntax": "JSONPATH",
                            "match": "$.behaviors[?(@.name == 'cpCode')].options.value.id"
                        }
                    }

        session = mockSessionObj()
        response = MockResponse()

        for mockJson in self.asyncAllsearchresponses:
            response.appendResponse(response.getJSONFromFile(mockJson))
            

        session.post.return_value = response
        session.get.return_value = response
        response.status_code = 202
        response.headers = { "Location" : "https://dummy.html"}

        edgerc = self.edgerc
        
        (_, json) = fetch.bulksearch(edgerc=edgerc, postdata=postdata, account_key=accountKey, contractId=contractId, network="Production", debug=False)

        self.assertEquals(1, len(json))
        results = json[0]["matchLocationResults"]
        self.assertEquals(1, len(results))
        self.assertEquals(12345,results[0])

        response.reset()



        

        for mapObj in self.asyncAllstagingresponseMaps:

            response.appendResponse( response.getJSONFromFile(mapObj["uri"]))
            response.appendResponseCode( mapObj["code"])

        fetch = PropertyManagerFetch(tempCache=True)
        (_, json) = fetch.bulksearch(edgerc=edgerc, postdata=postdata, account_key=accountKey, contractId=contractId, network="Staging", debug=False)

        self.assertEquals(1, len(json))
        results = json[0]["matchLocationResults"]
        self.assertEquals(2, len(results))

        self.assertEquals(12345, results[0])
        self.assertEquals(678910, results[1])
        
        results = json[0]["hostnames"]
        self.assertEquals(2, len(results))
        self.assertEquals("example1.com", results[0]["cnameFrom"] )
        self.assertEquals("m.example1.com", results[1]["cnameFrom"] )

        return json

    @patch('requests.Session')
    def testIntegration(self,  mockSessionObj):
        fetch = PropertyManagerFetch()

        accountKey="1-abcdef"
        
        contractId="ctr_C-0000"
        

        postdata = {
                        "bulkSearchQuery": {
                            "syntax": "JSONPATH",
                            "match": "$.behaviors[?(@.name == 'cpCode')].options.value.id"
                        }
                    }

        session = mockSessionObj()
        response = MockResponse()

        for mockJson in self.allsearchresponses:
            response.appendResponse(response.getJSONFromFile(mockJson))
            

        session.post.return_value = response
        session.get.return_value = response
        response.status_code = 200
        response.headers = {}

        edgerc = self.edgerc
        
        (_, json) = fetch.bulksearch(edgerc=edgerc, postdata=postdata, account_key=accountKey, contractId=contractId, network="Production", debug=False)

        self.assertEquals(1, len(json))
        results = json[0]["matchLocationResults"]
        self.assertEquals(1, len(results))
        self.assertEquals(12345,results[0])

        response.reset()
        
        response.status_code = 200

        for mockJson in self.allstagingresponses:
            response.appendResponse(response.getJSONFromFile(mockJson))

        (_, json) = fetch.bulksearch(edgerc=edgerc, postdata=postdata, account_key=accountKey, contractId=contractId, network="Staging", debug=False)

        self.assertEquals(1, len(json))
        results = json[0]["matchLocationResults"]
        self.assertEquals(2, len(results))

        self.assertEquals(12345, results[0])
        self.assertEquals(678910, results[1])
        

        return json

    

    @patch('requests.Session')
    @patch('bin.parse_commands.getArgFromSTDIN')
    def test_BulkSearchCommand(self,  getArgFromSTDIN, mockSessionObj):
        
        accountKey="1-abcdef"
        
        contractId="ctr_C-0000"
        

        postdata = {
                        "bulkSearchQuery": {
                            "syntax": "JSONPATH",
                            "match": "$.behaviors[?(@.name == 'cpCode')].options.value.id"
                        }
                    }

        
        postdata = json.dumps(postdata)
        getArgFromSTDIN.return_value = postdata

        session = mockSessionObj()
        response = MockResponse()
        commandTester = CommandTester(self)

        ## First Check
        for mockJson in self.asyncAllsearchresponses:
            response.appendResponse(response.getJSONFromFile(mockJson))
            

        session.post.return_value = response
        session.get.return_value = response
        response.status_code = 202
        response.headers = { "Location" : "https://dummy.html"}
        
        args = [
                "bulksearch",
                "--debug",
                "--section",
                "default",
                 "--edgerc",
                commandTester.edgeRc,
                "--use-searchstdin",
                "--contractId",
                contractId,
                "--account-key",
                accountKey,
                "--network",
                "production"

        ]

        stdOutResultArray = commandTester.wrapSuccessCommandStdOutOnly(func=main, args=args)
        
        self.assertEqual(2, len(stdOutResultArray) )

        header = stdOutResultArray[:1]
        header = json.loads(header[0])

        expectedHeaders = ['propertyName', 'results']

        self.assertIn(header[0], expectedHeaders)
        self.assertIn(header[1], expectedHeaders)

        values = stdOutResultArray[1:]

        values = list(map(lambda x: json.loads(x), values))

        self.assertEquals(1, len(values))
        self.assertEquals(12345,values[0][1])
        

        ## Next Check
        response.reset()
        response.status_code = 202

        for mockJson in self.asyncAllsearchresponses:
            response.appendResponse(response.getJSONFromFile(mockJson))


        args = [
                "bulksearch",
                "--section",
                "default",
                 "--edgerc",
                commandTester.edgeRc,
                "--contractId",
                contractId,
                "--account-key",
                accountKey,
                "--network",
                "production"

        ]

        stdOutResultArray = commandTester.wrapSuccessCommandStdOutOnly(func=main, args=args)
        
        header = stdOutResultArray[:1]
        header = json.loads(header[0])

        expectedHeaders = ['propertyName', 'results']

        self.assertIn(header[0], expectedHeaders)
        self.assertIn(header[1], expectedHeaders)

        values = stdOutResultArray[1:]

        values = list(map(lambda x: json.loads(x), values))

        self.assertEquals(1, len(values))
        self.assertEquals(12345,values[0][1])

        ## Next Check
        response.reset()
        response.status_code = 202

        for mockJson in self.asyncAllsearchresponses:
            response.appendResponse(response.getJSONFromFile(mockJson))


        args = [
                "bulksearch",
                "--section",
                "default",
                 "--edgerc",
                commandTester.edgeRc,
                "--contractId",
                contractId,
                "--account-key",
                accountKey,
                "--network",
                "production",
                "--searchname",
                "default.json"

        ]

        stdOutResultArray = commandTester.wrapSuccessCommandStdOutOnly(func=main, args=args)
        
        header = stdOutResultArray[:1]
        header = json.loads(header[0])

        expectedHeaders = ['propertyName', 'results']

        self.assertIn(header[0], expectedHeaders)
        self.assertIn(header[1], expectedHeaders)

        values = stdOutResultArray[1:]

        values = list(map(lambda x: json.loads(x), values))

        self.assertEquals(1, len(values))
        self.assertEquals(12345,values[0][1])
       

if __name__ == '__main__':
    unittest.main()



