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

from bin.fetch_cpcodes import CPCODEFetch


from unittest.mock import patch
from akamai.edgegrid import EdgeGridAuth, EdgeRc

from bin.lds_parse_commands import main 

class MockResponse:

    def __init__(self):
        self.status_code = None
        self.reset()
        
    def reset(self):
        self.jsonObj = []

    def appendResponse(self, obj):
        self.jsonObj.insert(0,obj)

    def json(self):

        if self.json is not None and len(self.jsonObj) > 0:
            return self.jsonObj.pop()
        else :
            raise Exception("no more mock responses")

        return self.jsonObj


class CPCODE_Test(unittest.TestCase):

    def loadTests(self, response):

        response.status_code = 200
        response.reset()
        response.appendResponse( self.getJSONFromFile( "{}/bin/tests/json/papi/_papi_v1_groups.json".format(os.getcwd()) ) )
        response.appendResponse( self.getJSONFromFile( "{}/bin/tests/json/papi/_papi_v1_cpcodes__ctr_1-1TJZFW_grp_41445.json".format(os.getcwd()) ) )
        response.appendResponse( self.getJSONFromFile( "{}/bin/tests/json/papi/_papi_v1_cpcodes__ctr_1-1TJZFW_grp_41444.json".format(os.getcwd()) ) )
        response.appendResponse( self.getJSONFromFile( "{}/bin/tests/json/papi/_papi_v1_cpcodes__ctr_1-1TJZFW_grp_41443.json".format(os.getcwd()) ) )
    
    def loadTests2(self, response):

        response.status_code = 200
        response.reset()
        response.appendResponse( self.getJSONFromFile( "{}/bin/tests/json/papi/_papi_v1_groups.multiple_contracts.json".format(os.getcwd()) ) )
        response.appendResponse( self.getJSONFromFile( "{}/bin/tests/json/papi/_papi_v1_cpcodes__ctr_1-1TJZFC_grp_441.json".format(os.getcwd()) ) )
        

    @patch('requests.Session')
    def testFetchGroupCPCODESWithContractIdFilter(self, mockSessionObj):

        saved_stdout = sys.stdout
        saved_stderr = sys.stderr

        try:

            out = StringIO()
            sys.stdout = out

            errout = StringIO()
            sys.stderr = errout

            response = MockResponse()
            self.loadTests2(response)

            session = mockSessionObj()
            session.get.return_value = response

            edgeRc = "{}/bin/tests/other/.dummy_edgerc".format(os.getcwd())

            fetch = CPCODEFetch()
            contractIds = ["ctr_0-1TJZFC"]
            (code, json) = fetch.fetchGroupCPCODES(edgerc = edgeRc, section="default", account_key=None, debug=False, onlycontractIds=contractIds)

            self.assertEqual(code, 200)
            self.assertEqual(len(json), 1)
            self.assertEqual(len(json[0]), 4)
            self.assertTrue( "cpcodes" in json[0] )
            self.assertTrue( "cpcodeId" in json[0]["cpcodes"][0] )
            self.assertTrue( "cpcodeName" in json[0]["cpcodes"][0] )
            
            self.assertEqual(json[0]["cpcodes"][0]["cpcodeId"], "cpc_33191")
            self.assertEqual(json[0]["cpcodes"][0]["cpcodeName"], "SME WAA")
       
        finally:

            sys.stdout = saved_stdout
            sys.stderr = saved_stderr     


    @patch('requests.Session')
    def testFetchGroupCPCODES(self, mockSessionObj):

        saved_stdout = sys.stdout
        saved_stderr = sys.stderr

        try:

            out = StringIO()
            sys.stdout = out

            errout = StringIO()
            sys.stderr = errout

            response = MockResponse()
            self.loadTests(response)

            session = mockSessionObj()
            session.get.return_value = response

            edgeRc = "{}/bin/tests/other/.dummy_edgerc".format(os.getcwd())

            fetch = CPCODEFetch()
            (code, json) = fetch.fetchGroupCPCODES(edgerc = edgeRc, section="default", account_key=None, debug=False)

            self.assertEqual(code, 200)
            self.assertEqual(len(json), 3)

            self.assertEqual(json[0]["cpcodes"][0]["cpcodeId"], "cpc_33192")
            self.assertEqual(json[0]["cpcodes"][0]["cpcodeName"], "SME WAA")

            self.assertEqual(json[1]["cpcodes"][0]["cpcodeId"], "cpc_33191")
            self.assertEqual(json[1]["cpcodes"][0]["cpcodeName"], "SME WAA")

            self.assertEqual(json[2]["cpcodes"][0]["cpcodeId"], "cpc_33190")
            self.assertEqual(json[2]["cpcodes"][0]["cpcodeName"], "SME WAA")

        finally:

            sys.stdout = saved_stdout
            sys.stderr = saved_stderr     


        self.loadTests2(response)

        args = [ "groupcpcodelist",
                "--section",
                "default",
                 "--edgerc",
                edgeRc,
                "--show-json",
                "--only-contractIds",
                "ctr_0-1TJZFC"

                ]

        (_, _, _, _) = self._testMainArgsAndGetResponseStdOutArray(args,1)

        self.loadTests(response)

        args = [ "groupcpcodelist",
                "--section",
                "default",
                 "--edgerc",
                edgeRc
                ]

        (_, _, _, _) = self._testMainArgsAndGetResponseStdOutArray(args,3)

        self.loadTests(response)

        args = [ "groupcpcodelist",
                "--section",
                "default",
                 "--edgerc",
                edgeRc,
                "--show-json"
                ]

        (_, _, _, _) = self._testMainArgsAndGetResponseStdOutArray(args,3)

      
        

    def _testMainArgsAndGetResponseStdOutArray(self, args, expectedStatusMsgs = 0):

        saved_stdout = sys.stdout
        saved_stderr = sys.stderr

        finaloutput = None

        try:
            out = StringIO()
            sys.stdout = out

            errout = StringIO()
            sys.stderr = errout
            
            mainresult = main(args)
            self.assertEqual(mainresult, 0, "command args {} should return successcode, but returned:\n+++++\n{}\n+++++\n".format(args,out.getvalue()) )

            output = list(out.getvalue().split("\n"))
            finaloutput = list(filter(lambda line: line != '', output))

            erroutput = list(errout.getvalue().split("\n"))
            finalerroutput = list(filter(lambda line: line != '', erroutput))

           
            self.assertGreater(len(finaloutput), 0, "command args {} and its output should be greater than zero".format(args) )
            self.assertEquals(len(finalerroutput), expectedStatusMsgs, "for args {} the std err message line count should be {} but got:\n {}".format(args,expectedStatusMsgs,erroutput) )

        except Exception as e:
            sys.stdout = saved_stdout
            sys.stderr = saved_stderr

            print(out.getvalue, sys.stdout)
            print(errout.getvalue, sys.stderr)
            raise e

        finally:
            
            sys.stdout = saved_stdout
            sys.stderr = saved_stderr

        return (output, finalerroutput, out, errout)   
    
    
    def getJSONFromFile(self, jsonPath):
            
            with open(jsonPath, 'r') as myfile:
                jsonStr = myfile.read()
            
            jsonObj = json.loads(jsonStr)
            return jsonObj

       

if __name__ == '__main__':
    unittest.main()



