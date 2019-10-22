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

    

    def test_list_Calcs(self):

        json_list = [
                        {
                            "startTime" : "2019-10-21T21:50:00Z",
                            "1xx" : 88
                        },
                        {
                            "startTime" : "2019-10-21T21:51:00Z",
                            "1xx" : 66
                        },
                        {
                            "startTime" : "2019-10-21T21:40:00Z",
                            "1xx" : 77
                        },
                        {
                            "startTime" : "2019-10-21T21:41:00Z",
                            "1xx" : 55
                        },
                        {
                            "startTime" : "2019-10-21T21:29:00Z",
                            "1xx" : 44
                        },
                        {
                            "startTime" : "2019-10-21T21:28:00Z",
                            "1xx" : 33
                        },
                        {
                            "startTime" : "2019-10-21T21:41:01Z",
                            "1xx" : 22
                        },
                        {
                            "startTime" : "2019-10-21T21:42:00Z",
                            "1xx" : 11
                        }
                      
                    ]
            
        
        json_data = {}
        json_data["data"] = json_list

        dataStreamFetch = DataStreamFetch()
        json_list = dataStreamFetch.sortAggregateList(json_list, "startTime")

        self.assertEqual("2019-10-21T21:28:00Z", json_list[0]["startTime"] )
        self.assertEqual("2019-10-21T21:29:00Z", json_list[1]["startTime"] )
        self.assertEqual("2019-10-21T21:40:00Z", json_list[2]["startTime"] )
        self.assertEqual("2019-10-21T21:51:00Z", json_list[7]["startTime"] )
        self.assertEqual(8, len(json_list) )

        
        pass

    def test_StartAndEnd_TimeRange_Calculations(self):
       
        dataStreamFetch = DataStreamFetch()
        currentEnd = datetime.datetime.utcnow()
        currentEndStr = dataStreamFetch.formatDatetoString(currentEnd)
        
        delta_2s = timedelta(seconds=2)
        delta_2m = timedelta(minutes=2)
        delta_2h = timedelta(hours=2)
        
        (start, resultingEnd) = dataStreamFetch.parseRange(currentEnd)
        self.assertEqual(currentEndStr, resultingEnd )
        expectedStart = currentEnd - delta_2m
        expectedStartStr = dataStreamFetch.formatDatetoString(expectedStart)
        self.assertEqual(expectedStartStr, start )

        (start, resultingEnd) = dataStreamFetch.parseRange(currentEnd, "2m")
        self.assertEqual(currentEndStr, resultingEnd )
        expectedStart = currentEnd - delta_2m
        expectedStartStr = dataStreamFetch.formatDatetoString(expectedStart)
        self.assertEqual(expectedStartStr, start )

        (start, resultingEnd) = dataStreamFetch.parseRange(currentEnd, "2s")
        self.assertEqual(currentEndStr, resultingEnd )
        expectedStart = currentEnd - delta_2s
        expectedStartStr = dataStreamFetch.formatDatetoString(expectedStart)
        self.assertEqual(expectedStartStr, start )

        (start, resultingEnd) = dataStreamFetch.parseRange(currentEnd, "2h")
        self.assertEqual(currentEndStr, resultingEnd )
        expectedStart = currentEnd - delta_2h
        expectedStartStr = dataStreamFetch.formatDatetoString(expectedStart)
        self.assertEqual(expectedStartStr, start )

        end = '2019-10-17T19:45:10Z'
        endDateObj = dataStreamFetch.createDatefromString(end)
        (new_start, new_end) = dataStreamFetch.parseRange(endDateObj, "2h")
        self.assertEqual(end, new_end)

        expectedStart = endDateObj - delta_2h
        expectedStartStr = dataStreamFetch.formatDatetoString(expectedStart)
        self.assertEqual(expectedStartStr, new_start )

        end = '2019-10-17T19:45:10Z'
        endDateObj = dataStreamFetch.createDatefromString(end)
        (new_start, new_end) = dataStreamFetch.parseRange(endDateObj, "2s")
        self.assertEqual(end, new_end)

        expectedStart = endDateObj - delta_2s
        expectedStartStr = dataStreamFetch.formatDatetoString(expectedStart)
        self.assertEqual(expectedStartStr, new_start )

        end = '2019-10-17T19:45:10Z'
        endDateObj = dataStreamFetch.createDatefromString(end)
        (new_start, new_end) = dataStreamFetch.parseRange(endDateObj, "2m")
        self.assertEqual(end, new_end)

        expectedStart = endDateObj - delta_2m
        expectedStartStr = dataStreamFetch.formatDatetoString(expectedStart)
        self.assertEqual(expectedStartStr, new_start )



