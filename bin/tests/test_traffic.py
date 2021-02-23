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
import json


from unittest.mock import patch
from akamai.edgegrid import EdgeGridAuth, EdgeRc

from bin.fetch_datastream import DataStreamFetch
from bin.fetch_datastream import utcDatefromString, daysSince

import datetime
from datetime import timedelta
from bin.credentialfactory import CredentialFactory

from bin.parse_commands import main 
from bin.tests.unittest_utils import CommandTester, MockResponse

from bin.send_analytics import Analytics 
from bin.fetch_traffic import TafficFetch


class Traffic_Test(unittest.TestCase):

    def disableTestDaysSince(self):
        
        fetch = TafficFetch()

        (code, _json) = fetch.fetchTrafficData(edgerc=None,section=None, account_key=None, objectIds=["123456"])
        print(json.dumps(_json, indent=1))
        self.assertEquals(200, code)
            

        
        

        


