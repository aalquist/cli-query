from io import StringIO
import json
import sys
import os

class CommandTester:

    def __init__(self, unittester):
        self.unittester = unittester
        self.edgeRc = "{}/bin/tests/other/.dummy_edgerc".format(os.getcwd())
    

    def wrapSuccessCommandStdOutOnly(self, func=None, args=[]):

        saved_stdout = sys.stdout
        saved_sterr = sys.stdout

        finaloutput = None

        try:
            out = StringIO()
            sys.stdout = out

            outerr = StringIO()
            sys.stderr = outerr
            
            returnVal = func(args)
            stdErrStr = outerr.getvalue()

            self.unittester.assertEqual(returnVal, 0, "command args {} should return successcode. Error msg: {}".format(args,stdErrStr) )

            output = list(out.getvalue().split("\n"))
            finaloutput = list(filter(lambda line: line != '', output))

           
            self.unittester.assertGreater(len(finaloutput), 0, "command args {} and its output should be greater than zero".format(args) )

            #sys.stdout = saved_stdout

        finally:
            sys.stdout = saved_stdout
            sys.stderr = saved_sterr

        self.unittester.assertIsNotNone(finaloutput)

        return finaloutput

class MockResponse:

    def __init__(self):
        self.status_code = None
        self.reset()
        
    def reset(self):
        self.jsonObj = []

    def appendResponse(self, obj):
        self.jsonObj.insert(0,obj)

    def getJSONFromFile(self, jsonPath):
            
            with open(jsonPath, 'r') as myfile:
                jsonStr = myfile.read()
            
            jsonObj = json.loads(jsonStr)
            return jsonObj

    def json(self):

        if self.json is not None and len(self.jsonObj) > 0:
            return self.jsonObj.pop()
        else :
            raise Exception("no more mock responses")

        return self.jsonObj


