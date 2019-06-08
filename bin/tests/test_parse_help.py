

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
from io import StringIO

from bin.lds_parse_commands import main 

class ParseCmdTest(unittest.TestCase):

    def test_main(self):

        args = [ "help"]
        #print("\n###testing args: {}".format(args))
        result, _ = self.redirectOutputToArray(lambda args : main(args) , args, False)
        self.assertTrue(len(result) > 0 )
        
        args = [ "help", "template"]
        #print("\n###testing args: {}".format(args))
        result, _ = self.redirectOutputToArray(lambda args : main(args) , args, False)
        self.assertTrue(len(result) > 0 )

        args = [ "help", "not_a_command"]
        #print("\n###testing args: {}".format(args))
        result, _ = self.redirectOutputToArray(lambda args : main(args) , args, True)
        self.assertTrue(len(result) == 0 )

        args = [ "help", "not_a_command"]
        #print("\n###testing args: {}".format(args))
        result, _ = self.redirectOutputToArray(lambda args : main(None) , args, True)
        self.assertTrue(len(result) == 0 )

        args = [ "help", "not_a_command"]
        #print("\n###testing args: {}".format(args))
        
        args = list([])
        result, _ = self.redirectOutputToArray(lambda args : main(args) , args, True)
        self.assertTrue(len(result) == 0 )


    def redirectOutputToArray(self, fun, value, ignoreNewLines = True):

        saved_stdout = sys.stdout
        out = StringIO()
        sys.stdout = out

        saved_stderr = sys.stderr
        outerr = StringIO()
        sys.stderr = outerr
        
        fun(value)

        output = list(out.getvalue().split("\n"))
        erroutput = list(outerr.getvalue().split("\n"))

        if ignoreNewLines:
            output = list(filter(lambda line: line != '', output))
            erroutput = list(filter(lambda line: line != '', erroutput))

        
        sys.stdout = saved_stdout
        sys.stderr = saved_stderr

        return (output, erroutput)
       

if __name__ == '__main__':
    unittest.main()


