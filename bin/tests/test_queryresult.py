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
import sys
import json

from bin.query_result import QueryResult


class QueryResultTest(unittest.TestCase):

    def testDefaultQueryLogic(self):
        queryresult = QueryResult("groupcpcodelist")
        templateJson = queryresult.getQuerybyName("doesnot_exist")
        self.assertNotIn("doesnot_exist", templateJson)
        
        self.assertRaises(Exception, queryresult.getQuerybyName, "doesnot_exist", throwErrorIfNotFound=True)
        pass
    
    def testCommandGeneric(self):
        
        queryresult = QueryResult("groupcpcodelist")
        RequireAll = True
        JoinValues = True
        ReturnHeader = False
        negativeMatch = False

        json = self.getJSONFromFile( "{}/bin/tests/json/_lds-api_v3_log-sources_cpcode-products.json".format(os.getcwd()) )

        dictObj = { "Status": "$[?(@.status=\"active\")].status"}

        #result = queryresult.parseCommandGeneric(json , dictObj, RequireAll, JoinValues, ReturnHeader)  
        #self.assertEqual(result[0][0], "active" )
        
        dictObj = { "Status": "$[?(@.status!=\"active\")].status"}
        result = queryresult.parseCommandGeneric(json , dictObj, RequireAll, JoinValues, ReturnHeader, negativeMatch)  
        self.assertEqual(result[0][0], "suspended" )

        pass 

        #suspended

        

    def getJSONFromFile(self, jsonPath):
        
        with open(jsonPath, 'r') as myfile:
            jsonStr = myfile.read()
        
        jsonObj = json.loads(jsonStr)
        return jsonObj

if __name__ == '__main__':
    unittest.main()