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


from bin.query_result import QueryResult
from bin.fetch_lds import LdsFetch
from bin.lds_parse_commands import main 

from unittest.mock import patch
from akamai.edgegrid import EdgeGridAuth, EdgeRc



class Template_Test(unittest.TestCase):

    
    def testTemplateTypes(self):

        args = [ "template"]

        saved_stdout = sys.stdout
        saved_stderr = sys.stderr

        finaloutput = None

        try:
            out = StringIO()
            sys.stdout = out
            
            outerr = StringIO()
            sys.stderr = outerr

            self.assertEqual(main(args), 0, "command args {} should return successcode".format(args) )

            output = list(out.getvalue().split("\n"))
            finaloutput = list(filter(lambda line: line != '', output))

           
            self.assertGreater(len(finaloutput), 0, "command args {} and its output should be greater than zero".format(args) )
            
            jsonStr=out.getvalue()
            jsondict = json.loads(jsonStr)  
            self.assertGreaterEqual( len(jsondict), 3 )
            self.assertIsInstance(jsondict, list)

            self.assertIn("ldslist", jsondict)
            self.assertIn("netstoragelist", jsondict)
            self.assertIn("alerts", jsondict)
            

        finally:
            pass
            sys.stdout = saved_stdout
            sys.stderr = saved_stderr

    def testTemplateNames(self):

        args = [ "template", "--type", "ldslist"]

        saved_stdout = sys.stdout
        saved_stderr = sys.stderr

        finaloutput = None

        try:
            out = StringIO()
            sys.stdout = out

            outerr = StringIO()
            sys.stderr = outerr
            
            self.assertEqual(main(args), 0, "command args {} should return successcode".format(args) )

            output = list(out.getvalue().split("\n"))
            finaloutput = list(filter(lambda line: line != '', output))

           
            self.assertGreater(len(finaloutput), 0, "command args {} and its output should be greater than zero".format(args) )
            
            jsonStr=out.getvalue()
            jsondict = json.loads(jsonStr)  
            self.assertGreaterEqual( len(jsondict), 3 )
            self.assertIsInstance(jsondict, list)
            
            self.assertIn("default.json", jsondict)
            self.assertIn("active-gpg.json", jsondict)
            self.assertIn("active.json", jsondict)
            

        finally:
            pass
            sys.stdout = saved_stdout
            sys.stderr = saved_stderr

    def testMainBootStrap(self):

       
        args = [
                "template",
                "--type",
                "ldslist",
                "--get",
                "active.json"  
            ]

        saved_stdout = sys.stdout
        saved_stderr = sys.stderr

        finaloutput = None

        try:
            out = StringIO()
            sys.stdout = out
            
            outerr = StringIO()
            sys.stderr = outerr

            self.assertEqual(main(args), 0, "command args {} should return successcode".format(args) )

            output = list(out.getvalue().split("\n"))
            finaloutput = list(filter(lambda line: line != '', output))

           
            self.assertGreater(len(finaloutput), 0, "command args {} and its output should be greater than zero".format(args) )
            
            jsondict = json.loads(out.getvalue())
            expected = self.getJSONFromFile( "{}/bin/queries/ldslist/active.json".format(os.getcwd()) )
            
            self.assertEqual( len(jsondict), len(expected) )

            for k in jsondict:
                self.assertEqual(jsondict[k], expected[k])

            args = [
                "template",
                "--type",
                "wrong_name",
                "--get",
                "default.json"  
            ]

            out = StringIO()
            sys.stdout = out

            outerr = StringIO()
            sys.stderr = outerr

            self.assertEqual(main(args), 1, "command args {} should NOT return successcode".format(args) )
            
            output = outerr.getvalue()
            self.assertAlmostEqual("template type: wrong_name not found. \n", output)
            
            jsonStr=out.getvalue()
            jsondict = json.loads(jsonStr)  
            self.assertGreaterEqual( len(jsondict), 3 )
            self.assertIsInstance(jsondict, list)

            self.assertIn("ldslist", jsondict)
            self.assertIn("netstoragelist", jsondict)
            self.assertIn("alerts", jsondict)
            
           
            

        finally:
            pass
            sys.stdout = saved_stdout
            sys.stderr = saved_stderr

        
    
    def getJSONFromFile(self, jsonPath):
            
            with open(jsonPath, 'r') as myfile:
                jsonStr = myfile.read()
            
            jsonObj = json.loads(jsonStr)
            return jsonObj

       

if __name__ == '__main__':
    unittest.main()



