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
import re
from io import StringIO


from bin.query_result import QueryResult
from bin.fetch_lds import LdsFetch
from bin.parse_commands import main

from bin.parse_commands import filtertemplate
from bin.tests.unittest_utils import CommandTester

from unittest.mock import patch
from akamai.edgegrid import EdgeGridAuth, EdgeRc

from bin.send_analytics import Analytics 


class Args:
    def __init__(self, show_json=False, type=None, use_stdin=False, file=None, template=None, arg_list=None, args_use_stdin=False, get=None):
        self.show_json=show_json
        self.use_stdin=use_stdin
        self.type=type
        self.file = file
        self.template = template
        self.arg_list = arg_list
        self.args_use_stdin = args_use_stdin
        self.get = get

class Template_Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        obj = Analytics()
        obj.disableAnalytics()

    @classmethod
    def tearDownClass(cls):
        obj = Analytics()
        obj.enableAnalytics()

    #getArgFromSTDIN
    @patch('bin.parse_commands.getArgFromSTDIN')
    def testTemplate(self, parseCommands):
        #--type ldslist --get cpcode-args.json --arg-list 123 456 --args-use-stdin
        args = Args(type="ldslist", get="arg-filter-active.json", arg_list=["123", "456"], args_use_stdin=True)

        parseCommands.return_value = "789"

        try:
            saved_stdout = sys.stdout
            saved_stderr = sys.stderr

            out = StringIO()
            sys.stdout = out
            
            outerr = StringIO()
            sys.stderr = outerr

            result = filtertemplate(args)

            outString = out.getvalue()
            jsonDict = json.loads(outString)
            
            self.assertIn("CPCODE", jsonDict)

            self.assertIn("123", jsonDict["CPCODE"] )
            self.assertIn("456", jsonDict["CPCODE"] )
            self.assertIn("789", jsonDict["CPCODE"] )

            #self.assertIn("Status", jsonDict)
            self.assertEqual(len(jsonDict), 1)

            errString = outerr.getvalue()
            self.assertEqual("",errString)
            self.assertEqual(0,result)


        finally:
            
            sys.stdout = saved_stdout
            sys.stderr = saved_stderr


    
    def testjSONPaths(self):

        
        template = QueryResult()

        jsonConfiguration = "$.logSource[#JSONPATHCRITERIA.cpCodeNumber#].cpCodeNumber"

        
        args = ["123", "456"]
        jsonPathGoal = "$.logSource[?(@.cpCodeNumber=\"123\"),?(@.cpCodeNumber=\"456\")].cpCodeNumber"
        result = template.extractAndReplaceCriteria(jsonConfiguration, args, ServerSide=False)
        self.assertEqual(jsonPathGoal, result)

        
        args = ["123"]
        jsonPathGoal = "$.logSource[?(@.cpCodeNumber=\"123\")].cpCodeNumber"
        result = template.extractAndReplaceCriteria(jsonConfiguration, args, ServerSide=False)
        self.assertEqual(jsonPathGoal, result)

        args = ["123"]
        jsonPathGoal = "$.logSource.cpCodeNumber"
        result = template.extractAndReplaceCriteria("$.logSource.cpCodeNumber", args, ServerSide=False)
        self.assertEqual(jsonPathGoal, result)

        args = ["cpCode", "origin"]
        jsonPathGoal = "$..behaviors[?(@.name=\"cpCode\"),?(@.name=\"origin\")].name"
        result = template.extractAndReplaceCriteria("$..behaviors[#JSONPATHCRITERIA.name#].name", args, ServerSide=False)
        self.assertEqual(jsonPathGoal, result)
    
    def testTemplateTypes(self):
        #filterfile = "{}/bin/tests/json/_storage_v1_storage-groups.json".format(os.getcwd())

        args = [ "filtertemplate"]

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
            
            

        finally:
            sys.stdout = saved_stdout
            sys.stderr = saved_stderr

    def testTemplateTypes_filterfile(self):
        
        filterfile = "{}/bin/queries/ldslist/default.json".format(os.getcwd())

        args = [ 
            "filtertemplate",
            "--filterfile",
            filterfile
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
            
            jsonStr=out.getvalue()
            jsondict = json.loads(jsonStr)  
            self.assertIsInstance(jsondict, dict)

            self.assertIn("CPCODE", jsondict)
            self.assertIn("Aggregation_Frequency", jsondict)
            self.assertIn("Directory", jsondict)
            
            

        finally:
            sys.stdout = saved_stdout
            sys.stderr = saved_stderr

    def testTemplateNames(self):

        args = [ "filtertemplate", "--type", "ldslist"]

        saved_stdout = sys.stdout
        saved_stderr = sys.stderr

        finaloutput = None

        try:
            out = StringIO()
            sys.stdout = out

            outerr = StringIO()
            sys.stderr = outerr
            result = main(args)

            

            output = list(out.getvalue().split("\n"))
            finaloutput = list(filter(lambda line: line != '', output))

            self.assertEqual(result, 0, "command args {} should return successcode".format(args) )
           
            self.assertGreater(len(finaloutput), 0, "command args {} and its output should be greater than zero".format(args) )
            
            jsonStr=out.getvalue()
            jsondict = json.loads(jsonStr)  
            self.assertGreaterEqual( len(jsondict), 3 )
            self.assertIsInstance(jsondict, list)
            
            self.assertIn("default.json", jsondict)
            self.assertIn("active-gpg.json", jsondict)
            self.assertIn("all-default.json", jsondict)
            

        finally:
            pass
            sys.stdout = saved_stdout
            sys.stderr = saved_stderr

    def testMainBootStrap(self):

       
        args = [
                "filtertemplate",
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

            for k in jsondict:
                filename = "{}/bin/queries/ldslist/{}".format(os.getcwd(),k)
                self.assertTrue(  os.path.exists(filename) and os.path.isfile(filename))

            args = [
                "filtertemplate",
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
           
            
           
            

        finally:
            pass
            sys.stdout = saved_stdout
            sys.stderr = saved_stderr

    def testSearchTemplate(self):

        commandTester = CommandTester(self)

        args = [
                "bulksearchtemplate",
                "--get",
                "default.json"
        ]

        stdOutResultArray = commandTester.wrapSuccessCommandStdOutOnly(func=main, args=args)
        stdOutString = os.linesep.join(stdOutResultArray)
        stdOutJSONDict = json.loads(stdOutString)

        self.assertIn("bulkSearchQuery", stdOutJSONDict)

        ##Next Test

        commandTester = CommandTester(self)

        args = [
                "bulksearchtemplate"
                
        ]

        stdOutResultArray = commandTester.wrapSuccessCommandStdOutOnly(func=main, args=args)
        stdOutString = os.linesep.join(stdOutResultArray)
        stdOutJSONDict = json.loads(stdOutString)

        self.assertIsInstance(stdOutJSONDict, list)

    def testSearchTemplate_withArgs(self):

        ##Next Test

        commandTester = CommandTester(self)

        args = [
                "bulksearchtemplate",
                "--get",
                "arg-behavior-by-name.json",
                "--arg-list",
                "origin"
        ]

        stdOutResultArray = commandTester.wrapSuccessCommandStdOutOnly(func=main, args=args)
        stdOutString = os.linesep.join(stdOutResultArray)
        stdOutJSONDict = json.loads(stdOutString)

        self.assertIn("bulkSearchQuery", stdOutJSONDict)
        self.assertIn("match", stdOutJSONDict["bulkSearchQuery"])

        self.assertEquals(stdOutJSONDict["bulkSearchQuery"]["match"], "$..behaviors[?(@.name == 'origin')].name" )
       

        ##Next Test

        commandTester = CommandTester(self)

        args = [
                "bulksearchtemplate",
                "--get",
                "arg-behavior-by-name.json",
                "--arg-list",
                "origin",
                "cpCode"
        ]

        stdOutResultArray = commandTester.wrapSuccessCommandStdOutOnly(func=main, args=args)
        stdOutString = os.linesep.join(stdOutResultArray)
        stdOutJSONDict = json.loads(stdOutString)

        self.assertIn("bulkSearchQuery", stdOutJSONDict)
        self.assertIn("match", stdOutJSONDict["bulkSearchQuery"])

        self.assertEquals(stdOutJSONDict["bulkSearchQuery"]["match"], "$..behaviors[?(@.name == 'origin') || ?(@.name == 'cpCode')].name" )

        ##Next Test

        commandTester = CommandTester(self)

        searchfile = "{}/bin/queries/bulksearch/serverside/arg-behavior-by-name.json".format(os.getcwd())

        args = [
                "bulksearchtemplate",
                "--searchfile",
                searchfile,
                "--arg-list",
                "origin",
                "cpCode"
        ]

        stdOutResultArray = commandTester.wrapSuccessCommandStdOutOnly(func=main, args=args)
        stdOutString = os.linesep.join(stdOutResultArray)
        stdOutJSONDict = json.loads(stdOutString)

        self.assertIn("bulkSearchQuery", stdOutJSONDict)
        self.assertIn("match", stdOutJSONDict["bulkSearchQuery"])

        self.assertEquals(stdOutJSONDict["bulkSearchQuery"]["match"], "$..behaviors[?(@.name == 'origin') || ?(@.name == 'cpCode')].name" )
        
    
    def getJSONFromFile(self, jsonPath):
            
            with open(jsonPath, 'r') as myfile:
                jsonStr = myfile.read()
            
            jsonObj = json.loads(jsonStr)
            return jsonObj

       

if __name__ == '__main__':
    unittest.main()



