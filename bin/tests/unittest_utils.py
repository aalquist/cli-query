from io import StringIO
import json
import sys
import os
from pathlib import Path

class CommandTester:

    def __init__(self, unittester):
        self.unittester = unittester
        self.edgeRc = "{}/bin/tests/other/.dummy_edgerc".format(os.getcwd())
    

    def wrapSuccessCommandStdOutOnly(self, func=None, args=[], expectedReturnCode=0, assertMinStdOutLines=1):

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

            self.unittester.assertEqual(returnVal, expectedReturnCode, "command args {} should return successcode. Error msg: {}".format(args,stdErrStr) )

            output = list(out.getvalue().split("\n"))
            finaloutput = list(filter(lambda line: line != '', output))

           
            self.unittester.assertGreater(len(finaloutput), assertMinStdOutLines-1, "command args {} and its output should be greater than zero".format(args) )

            #sys.stdout = saved_stdout

        finally:
            sys.stdout = saved_stdout
            sys.stderr = saved_sterr

        self.unittester.assertIsNotNone(finaloutput)

        return finaloutput

class MockResponse:

    def __init__(self):
        self.reset()
        
    def reset(self):
        self.jsonObj = []
        self.code = None

    def appendResponse(self, obj):
        self.jsonObj.insert(0,obj)

    def appendResponseCode(self, obj):
        
        if self.code is None:
            self.code = list()

        if isinstance(self.code, list):
            self.code.insert(0,obj)

        else:
            raise Exception("can't append to non list")

    def getJSONFromFile(self, jsonPath):
            
            readPath = Path(jsonPath)

            if os.name == 'nt':
                print(readPath)

            with open(readPath, 'r') as myfile:
                jsonStr = myfile.read()
            
            if os.name == 'nt':
                print(jsonStr)

            jsonObj = json.loads(jsonStr)
            return jsonObj

    def json(self):

        if self.json is not None and len(self.jsonObj) > 0:
            obj = self.jsonObj.pop()
            #print(" ... popping mock json obj" , file=sys.stderr )
            return obj

        else:
            raise Exception("no more mock responses")

        return self.jsonObj

    @property
    def status_code(self):

        if self.code is not None and isinstance(self.code, list) and len(self.code) > 0:
            code = self.code.pop()
            #print(" ... popping mock code {}".format(code) , file=sys.stderr )
            return code

        elif self.code is not None and not isinstance(self.code, list):
            return self.code

        else:
            raise Exception("no more mock code responses")

        return self.code

    @status_code.setter
    def status_code(self, newValue):
        self.code = newValue 
    

