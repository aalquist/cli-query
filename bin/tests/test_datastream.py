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


from unittest.mock import patch
from akamai.edgegrid import EdgeGridAuth, EdgeRc

from bin.fetch_datastream import DataStreamFetch

import datetime
from datetime import timedelta



class DataStream_Test(unittest.TestCase):

    def test_StartAndEnd_TimeRange_Calculations(self):
       
        dataStreamFetch = DataStreamFetch()
        start = datetime.datetime.utcnow()

        delta_2s = timedelta(seconds=2)
        delta_2m = timedelta(minutes=2)
        delta_2h = timedelta(hours=2)
        
        (_, end) = dataStreamFetch.parseRange(start)
        expectedEnd = start + delta_2m
        expectedEndStr = dataStreamFetch.formatDatetoString(expectedEnd)
        self.assertEqual(expectedEndStr, end )

        (_, end) = dataStreamFetch.parseRange(start, "2m")
        expectedEnd = start + delta_2m
        expectedEndStr = dataStreamFetch.formatDatetoString(expectedEnd)
        self.assertEqual(expectedEndStr, end )

        (_, end) = dataStreamFetch.parseRange(start, "2s")
        expectedEnd = start + delta_2s
        expectedEndStr = dataStreamFetch.formatDatetoString(expectedEnd)
        self.assertEqual(expectedEndStr, end )

        (_, end) = dataStreamFetch.parseRange(start, "2h")
        expectedEnd = start + delta_2h
        expectedEndStr = dataStreamFetch.formatDatetoString(expectedEnd)
        self.assertEqual(expectedEndStr, end )
        
        start = '2019-10-17T19:45:10Z'
        startDateObj = dataStreamFetch.createDatefromString(start)
        (new_start, end) = dataStreamFetch.parseRange(start, "2h")
        self.assertEqual(start, new_start )

        expectedEnd = startDateObj + delta_2h
        expectedEndStr = dataStreamFetch.formatDatetoString(expectedEnd)
        self.assertEqual(expectedEndStr, end)



