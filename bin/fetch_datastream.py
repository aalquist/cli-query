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

from akamai.edgegrid import EdgeGridAuth, EdgeRc

from bin.credentialfactory import CredentialFactory
from bin.fetch import Fetch_Akamai_OPENAPI_Response

import datetime
from datetime import timedelta
import pytz
import re
import sys

def utcDatefromString(start):
    format = '%Y-%m-%dT%H:%M:%SZ'
    d = datetime.datetime.strptime(start, format)
    d.replace(tzinfo=pytz.UTC)
    return d

def daysSince(priorDate, now=None):
    
    priorDate = utcDatefromString(priorDate)

    if now is None:
        now = datetime.datetime.utcnow()
    
    delta = now - priorDate
    days = delta.days
    return days

class DataStreamFetch(Fetch_Akamai_OPENAPI_Response):

    def formatDatetoString(self, dateobj):
        timeformat = "%Y-%m-%dT%H:%M:%SZ"
        return dateobj.strftime(timeformat)

    
    def createDatefromString(self, start):
        return utcDatefromString(start)
        

    def parseRange(self, end=None, timerange="2m", offsetMinutes=1):
        regex = r"(\d+)([msh])"
        matches = re.search(regex, timerange, re.IGNORECASE | re.DOTALL)

        if matches:
            g = matches.groups()
            rangeVal = int(g[0])
            rangeUnit = g[1]

            if rangeUnit == "m" :
                delta = timedelta(minutes=rangeVal)
            elif rangeUnit == "s":
                delta = timedelta(seconds=rangeVal)
            elif rangeUnit == "h":
                delta = timedelta(hours=rangeVal)
            else:
                raise ValueError("rangeUnit {} is not valid".format(rangeUnit) )

            if end is None:
                end = datetime.datetime.utcnow()

            elif not isinstance(end, datetime.date) :
                end = self.createDatefromString(end)

            offset = timedelta(minutes=offsetMinutes)
            offsetEnd = end - offset
            
            start = offsetEnd - delta
            print("UTC Start: {} UTC End: {}".format(start, offsetEnd), file=sys.stderr )
            return (self.formatDatetoString(start), self.formatDatetoString(offsetEnd) )

    def buildStreamUrl(self, context, *, streamId=None, logType="raw", timerange=None, offsetMinutes=1):
        
        if streamId is None:
            raise ValueError("streamId is required")

        if logType not in ["raw", "aggregate"]:
            raise ValueError("log type must be either raw or aggregate")


        url = self.buildUrl("https://{}/datastream-pull-api/v1/streams/{}/{}-logs", context, streamId, logType)

        if timerange is None:
            (startTime, endTime) = self.parseRange(offsetMinutes=offsetMinutes)

        else:
            (startTime, endTime) = self.parseRange(timerange=timerange, offsetMinutes=offsetMinutes)

        queryArgs = [("start", startTime), ("end", endTime)]

        url = self.appendQueryStringTupple(url, queryArgs)
        return url

    def convertReponseCodeObjName(self, jsonElement, codeName):

        if codeName in jsonElement:
            obj = jsonElement[codeName]
            del jsonElement[codeName]
            jsonElement["code_{}".format(codeName)] = obj
                    
        return jsonElement

    def sortAggregateList(self, returnedList, sortBy):
        
        returnedList = sorted(returnedList, key=lambda x : x[sortBy] )
        return returnedList

    def fetchLogs(self, *, edgerc, section, streamId=None, startTime=None, timeRange=None, logType="raw", offsetMinutes=1, debug=False):

        factory = CredentialFactory()
        context = factory.load(edgerc, section, None)
        
        url = self.buildStreamUrl(context, streamId=streamId, logType=logType, timerange=timeRange, offsetMinutes=offsetMinutes)
        
        if debug:
            print(" ... Getting Url: {}".format(url), file=sys.stderr )

        result = context.session.get(url)
        code, json = self.handleResponse(result, url, debug)

        if code in [200] and "data" in json:
            json = json["data"]

            if logType == "aggregate":
               
                #why? JSONPath doesn't like indexes that start with numbers. changing the index names is easier than the alternatives
                for j in json:
                    self.convertReponseCodeObjName(j, "1xx")
                    self.convertReponseCodeObjName(j, "2xx")
                    self.convertReponseCodeObjName(j, "3xx")
                    self.convertReponseCodeObjName(j, "4xx")
                    self.convertReponseCodeObjName(j, "5xx")
                
                json = self.sortAggregateList( json, "startTime")

            return (code, json)
        else:
            return (code, json)

    
        
    