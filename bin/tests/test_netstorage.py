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
from bin.fetch_lds import LdsFetch
from bin.lds_parse_commands import main 

from unittest.mock import patch
from akamai.edgegrid import EdgeGridAuth, EdgeRc

class MockResponse:

    def __init__(self):
        self.status_code = None
        self.jsonObj = None

    def json(self):
        return self.jsonObj


class NetStorage_Test(unittest.TestCase):

    @patch('requests.Session')
    def testParseMain_fetchNetStorageGroups(self, mockSessionObj):

        response = MockResponse()
        response.status_code = 200
        response.jsonObj = self.getJSONFromFile( "{}/bin/tests/json/_storage_v1_storage-groups.json".format(os.getcwd()) )

        session = mockSessionObj()
        session.get.return_value = response

        edgeRc = "{}/bin/tests/other/.dummy_edgerc".format(os.getcwd())

        args = [ "netstoragelist",
                "--section",
                "default",
                 "--edgerc",
                edgeRc,
                "--show-json"
                ]

        (_, _) = self._testMainArgsAndGetResponseStdOutArray(args)
        


        args = [ "netstoragelist",
                "--section",
                "default",
                 "--edgerc",
                edgeRc,
                "--template",
                "default.json",
                "--debug"
                
                ]

        (_, _) = self._testMainArgsAndGetResponseStdOutArray(args)


        args = [ "netstoragelist",
                "--section",
                "default",
                 "--edgerc",
                edgeRc,
                "--file",
                "{}/bin/queries/netstoragelist/default.json".format(os.getcwd()),
                "--debug"
                
                ]

        (_, _) = self._testMainArgsAndGetResponseStdOutArray(args)

        args = [ "netstoragelist",
                "--section",
                "default",
                 "--edgerc",
                edgeRc,
                "--debug"
                
                ]

        (_, _) = self._testMainArgsAndGetResponseStdOutArray(args)

    @patch('requests.Session')
    def testParseMain_fetchNetStorageUsers(self, mockSessionObj):

        response = MockResponse()
        response.status_code = 200
        
        response.jsonObj = self.getJSONFromFile( "{}/bin/tests/json/_storage_v1_upload-accounts.json".format(os.getcwd()) )

        session = mockSessionObj()
        session.get.return_value = response

        edgeRc = "{}/bin/tests/other/.dummy_edgerc".format(os.getcwd())

        args = [ "netstorageuser",
                "--section",
                "default",
                 "--edgerc",
                edgeRc,
                "--show-json"
                ]

        (_, stdOut) = self._testMainArgsAndGetResponseStdOutArray(args)
        jsonStr = stdOut.getvalue()
        jsonObj = json.loads(jsonStr)

        self.assertEqual(len(jsonObj), 1)
        self.assertEqual(jsonObj[0]["asperaEnabled"], True)

        args = [ "netstorageuser",
                "--section",
                "default",
                 "--edgerc",
                edgeRc
                ]

        (outputArray, _) = self._testMainArgsAndGetResponseStdOutArray(args)
        
        jsonObj = json.loads(outputArray[0],object_pairs_hook=OrderedDict)
        #jsonObj.sort()

        self.assertEqual(len(jsonObj), 10)
        
        dataset = ["StorageGroupId", "Email"]
        jsonObj.sort()
        self.assertIn(jsonObj[0],dataset)
        self.assertIn(jsonObj[1],dataset)

        jsonObj = json.loads(outputArray[1],object_pairs_hook=OrderedDict)
        

        dataset = [1234568, "some_netstorage_groupname_missing_in_doc", "your@email.com"]
        self.assertIn(jsonObj[0],dataset)
        self.assertIn(jsonObj[1],dataset)
        self.assertIn(jsonObj[2],dataset)


        

        pass

       


    def _testMainArgsAndGetResponseStdOutArray(self, args):

        saved_stdout = sys.stdout
        finaloutput = None

        try:
            out = StringIO()
            sys.stdout = out
            
            self.assertEqual(main(args), 0, "command args {} should return successcode, but returned:\n+++++\n{}\n+++++\n".format(args,out.getvalue()) )

            output = list(out.getvalue().split("\n"))
            finaloutput = list(filter(lambda line: line != '', output))

           
            self.assertGreater(len(finaloutput), 0, "command args {} and its output should be greater than zero".format(args) )
            
            sys.stdout = saved_stdout


        finally:
            pass
            sys.stdout = saved_stdout

        return (output, out)
    
    def getJSONFromFile(self, jsonPath):
            
            with open(jsonPath, 'r') as myfile:
                jsonStr = myfile.read()
            
            jsonObj = json.loads(jsonStr)
            return jsonObj

       

if __name__ == '__main__':
    unittest.main()



