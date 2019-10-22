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

import datetime
from datetime import timedelta
from bin.credentialfactory import CredentialFactory

from bin.parse_commands import main 
from bin.tests.unittest_utils import CommandTester, MockResponse



class DataStream_Test(unittest.TestCase):

    def setUp(self):
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        self.edgerc = "{}/other/.dummy_edgerc".format(self.basedir)
        self.aggregate_logs = [
            "{}/json/datastream-aggregate/all-aggregate-logs.json".format(self.basedir)
        ]

        self.raw_logs = [
            "{}/json/datastream-raw/all-raw-logs.json".format(self.basedir)
        ]

    def test_ConvertResponseCodeObjectKeys(self):

        dataStreamFetch = DataStreamFetch()
        dataStreamFetch.convertReponseCodeObjName

        testJSON = {
            "1xx" : 1,
            "2xx" : 2,
            "3xx" : 3,
            "4xx" : 4,
            "5xx" : 5
        }

        jObj = dataStreamFetch.convertReponseCodeObjName(testJSON, "1xx")
        self.assertTrue( "code_1xx" in jObj)
        self.assertEquals( 1, jObj["code_1xx"])

        jObj = dataStreamFetch.convertReponseCodeObjName(testJSON, "2xx")
        self.assertTrue( "code_2xx" in jObj)
        self.assertEquals( 2, jObj["code_2xx"])

        jObj = dataStreamFetch.convertReponseCodeObjName(testJSON, "3xx")
        self.assertTrue( "code_3xx" in jObj)
        self.assertEquals( 3, jObj["code_3xx"])

        jObj = dataStreamFetch.convertReponseCodeObjName(testJSON, "4xx")
        self.assertTrue( "code_4xx" in jObj)
        self.assertEquals( 4, jObj["code_4xx"])

        jObj = dataStreamFetch.convertReponseCodeObjName(testJSON, "5xx")
        self.assertTrue( "code_5xx" in jObj)
        self.assertEquals( 5, jObj["code_5xx"])


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

        end = '2019-10-17T19:45:10Z'
        (new_start, new_end) = dataStreamFetch.parseRange(end, "2s")
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

    @patch('requests.Session')
    def test_DataStreamAggregateMockAPI(self, mockSessionObj):
        session = mockSessionObj()
        response = MockResponse()

        for mockJson in self.aggregate_logs:
            response.appendResponse(response.getJSONFromFile(mockJson))
            
        session.post.return_value = response
        session.get.return_value = response
        response.status_code = 200
        response.headers = {}
        
        commandTester = CommandTester(self)

        args = [
                "datastream_agg",
                "--debug",
                "--section",
                "default",
                 "--edgerc",
                commandTester.edgeRc,
                "--streamId",
                "0007",
                "--timeRange",
                "20m"
        ]

        stdOutResultArray = commandTester.wrapSuccessCommandStdOutOnly(func=main, args=args)

        self.assertEqual(6, len(stdOutResultArray) )

        header = stdOutResultArray[:1]
        header = json.loads(header[0])

        expectedHeaders = ["startTime", "1xx", "2xx", "3xx", "4xx", "5xx", "endTime"]
        startTime = header[0]

        self.assertIn(startTime, expectedHeaders)

        values = stdOutResultArray[1:]

        expectedStartTimes = [ "2019-03-13T02:00:00Z", "2019-03-13T02:37:00Z", "2019-03-13T03:13:00Z", "2019-03-13T04:31:00Z", "2019-03-13T04:56:00Z"]


        for j in values:

            row = json.loads(j)
            self.assertIn(row[0], expectedStartTimes)
    
    @patch('requests.Session')
    def test_DataStreamRAWMockAPI(self, mockSessionObj):
        session = mockSessionObj()
        response = MockResponse()

        for mockJson in self.raw_logs:
            response.appendResponse(response.getJSONFromFile(mockJson))
            
        session.post.return_value = response
        session.get.return_value = response
        response.status_code = 200
        response.headers = {}
        
        commandTester = CommandTester(self)

        args = [
                "datastream_raw",
                "--debug",
                "--section",
                "default",
                 "--edgerc",
                commandTester.edgeRc,
                "--streamId",
                "0007",
                "--timeRange",
                "20m"
        ]

        stdOutResultArray = commandTester.wrapSuccessCommandStdOutOnly(func=main, args=args)

        self.assertEqual(3, len(stdOutResultArray) )

        header = stdOutResultArray[:1]
        header = json.loads(header[0])

        print(header)

        expectedHeaders = ['CPCODE', 'ResponseCode', 'Method', 'Protocol', 'Host', 'Path']
        CPCODE = header[0]

        self.assertIn(CPCODE, expectedHeaders)

        values = stdOutResultArray[1:]

        for j in values:
            json.loads(j)
            

        
        

        


