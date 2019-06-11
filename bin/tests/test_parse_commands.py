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
import collections
import os
import sys
from bin.lds_parse_commands import handleresponse 
from bin.query_result import QueryResult

class Args:
    def __init__(self, show_json=False, use_stdin=False, file=None, template=None):
        self.show_json=show_json
        self.use_stdin=use_stdin
        self.file = file
        self.template = template


class Test_Lds_Parse_Commands(unittest.TestCase):

    def testHandleResponse(self):

        args = Args(template="Test_12313123")
        queryresult = QueryResult("ldslist")

        with self.assertRaises(Exception) as cm:  
            handleresponse(args, {}, queryresult)
        the_exception = cm.exception  
        self.assertIn("Test_12313123", the_exception.args[0])
        self.assertIn("not found", the_exception.args[0])  
        
    
        
        


if __name__ == '__main__':
    unittest.main()