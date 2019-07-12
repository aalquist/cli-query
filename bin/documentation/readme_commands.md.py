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

import os
import sys
import json
from io import StringIO

SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
PACKAGE_PARENT = '../..'
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from bin.parse_commands import main 


class GenerateReadMeCommands():

    def main(self):

        os.environ['AKAMAI_CLI'] = "True"

        print("## Help Text")
        args = [ "help"]
        result, _ = self.redirectOutputToArray(lambda args : main(args) , args, False)
        self.printHelpTest(result.getvalue())
        
        print("## Template Utility")
        args = [ "help", "template"]
        result, _ = self.redirectOutputToArray(lambda args : main(args) , args, False)
        print(result.getvalue())

        print("## Querying LDS")
        args = [ "help", "ldslist"]
        result, _ = self.redirectOutputToArray(lambda args : main(args) , args, False)
        self.printHelpTest(result.getvalue())

        print("## Querying Netstorage NS4")
        args = [ "help", "netstoragelist"]
        result, _ = self.redirectOutputToArray(lambda args : main(args) , args, False)
        self.printHelpTest(result.getvalue())
        
        print("## Querying Netstorage Users")
        args = [ "help", "netstorageuser"]
        result, _ = self.redirectOutputToArray(lambda args : main(args) , args, False)
        self.printHelpTest(result.getvalue())

        print("## Querying Control Center Group CPCodes")
        args = [ "help", "groupcpcodelist"]
        result, _ = self.redirectOutputToArray(lambda args : main(args) , args, False)
        self.printHelpTest(result.getvalue())

        print("## Querying Property Mangager Configurations")
        args = [ "help", "bulksearch"]
        result, _ = self.redirectOutputToArray(lambda args : main(args) , args, False)
        self.printHelpTest(result.getvalue())

        print("## Bulk Search Template Utility")
        args = [ "help", "bulksearchtemplate"]
        result, _ = self.redirectOutputToArray(lambda args : main(args) , args, False)
        self.printHelpTest(result.getvalue())
        


    def printHelpTest(self, value):
        print()
        print("```bash ")
        print(value)
        print("```")


    def redirectOutputToArray(self, fun, value, ignoreNewLines = True):

        saved_stdout = sys.stdout
        out = StringIO()
        sys.stdout = out

        saved_stderr = sys.stderr
        outerr = StringIO()
        sys.stderr = outerr
        
        _ = fun(value)

        sys.stdout = saved_stdout
        sys.stderr = saved_stderr

        return (out, outerr)
       

if __name__ == '__main__':
    prog = GenerateReadMeCommands()
    prog.main()


