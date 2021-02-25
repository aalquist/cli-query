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

class TafficFetch(Fetch_Akamai_OPENAPI_Response):

    def isFloat(self, floatnum):  
  
        regex = r"^[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?$"
        return re.search(regex, floatnum)  
            
    def convertNum(self, item):

        if isinstance(item, str) and "." not in item and item.isdigit(): 
            return int(item)

        elif isinstance(item, str) and self.isFloat(item):
            try:
                return float(item)

            except ValueError:
                return int(item)

        else:
            return item

    def convert_strings_to_numbers(self, params):
        for key in params.keys():
            if isinstance(params[key], dict):
                self.convert_strings_to_numbers(params[key])
            elif isinstance(params[key], list):
                for item in params[key]:
                    if not isinstance(item, (dict, list)):
                        
                        item = self.convertNum(item)
                    else:
                        self.convert_strings_to_numbers(item)
            else:
                params[key] = self.convertNum(params[key])
        return params

    def formatDatetoString(self, dateobj):
        timeformat = "%Y-%m-%dT%H:%M:%SZ"
        return dateobj.strftime(timeformat)

    
    def createDatefromString(self, start):
        return utcDatefromString(start)
        

    def parseRange(self, end=None, timerange="2d", offsetMinutes=1):
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
            return (self.formatDatetoString(start), self.formatDatetoString(offsetEnd) )

    def getPriorDayRange(self):
        
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        base = yesterday

        date_list = [base - datetime.timedelta(days=x) for x in range(2)]
        start = date_list[1]
        end = date_list[0]
        return (start, end)

    
    def buildUrlTrafficUrl(self, context, objectIds=None, startDate=None, endDate=None):
        
        #/reporting-api/v1/reports/hits-by-cpcode/versions/1/report-data objectIds==367155 start==2021-02-18T00:00:00Z end==2021-02-22T09:00:00Z

        assert objectIds is not None and len(objectIds) > 0
        objectIds = ",".join(objectIds)

        assert startDate is not None
        assert endDate is not None

        url = self.buildUrl("https://{}/reporting-api/v1/reports/hits-by-cpcode/versions/1/report-data?objectIds={}", context, objectIds)

        if not isinstance(startDate, str):
            startDate = str(startDate)
        
        if not isinstance(endDate, str):
            endDate = str(endDate)

        queryArgs = [("start", "{}T00:00:00Z".format(startDate)), ("end", "{}T09:00:00Z".format(endDate))]

        url = self.appendQueryStringTupple(url, queryArgs)
        return url

    def fetchTrafficDataJsonArray(self, *, edgerc, section, account_key=None, jsonObjectList=[], cpCodeIndex=1, startDate=None, endDate=None, debug=False):
        
        returnTupleList = list()

        for jsonObject in jsonObjectList:

            if isinstance(jsonObject, list):

                if len(jsonObject) >= cpCodeIndex:
                    objectIds = jsonObject[cpCodeIndex]
                    objectIds = list(map(lambda x : str(x), objectIds))
                    (code, _json) = self.fetchTrafficData(edgerc=edgerc, section=section, account_key=account_key, objectIds=objectIds, startDate=startDate, endDate=endDate, debug=debug)
                    returnTupleList.append( (code, _json) )

                    if debug:
                        print(f"  ... Got response code: {code}", file=sys.stderr )
                else:
                    (599, {"error" : "cpCodeIndex index out of bounds"}) 
                    returnTupleList.append( (code, _json) )
                    break

            else:
                (599, {"error" : "input not a list"}) 
                returnTupleList.append( (code, _json) )
                break


        all200 = all(list(map(lambda x : x[0] == 200, returnTupleList)))
        results = list(map(lambda x : (x[1]), returnTupleList))
        
        

        if all200:
            responseCode = 200
        else:
            responseCode = 500

        return (responseCode, results)

    def fetchTrafficDataList(self, *, edgerc, section, account_key=None, objectIdMatrix=[], startDate=None, endDate=None, debug=False):

        returnTupleList = list()

        for objectId in objectIdMatrix:

            if isinstance(objectId, list):
                (code, _json) = self.fetchTrafficData(edgerc=edgerc, section=section, account_key=account_key, objectIds=objectId, startDate=startDate, endDate=endDate, debug=debug)
                returnTupleList.append( (code, _json) )
            
            else:
                (code, _json) = self.fetchTrafficData(edgerc=edgerc, section=section, account_key=account_key, objectIds=[objectId], startDate=startDate, endDate=endDate, debug=debug)
                returnTupleList.append( (code, _json) )

        all200 = all(list(map(lambda x : x[0] == 200, returnTupleList)))
        results = list(map(lambda x : x[1], returnTupleList))

        if all200:
            responseCode = 200
        else:
            responseCode = 500

        return (responseCode, results)
           


    def fetchTrafficData(self, *, edgerc, section, account_key=None, objectIds=[], startDate=None, endDate=None, debug=False):

        factory = CredentialFactory()
        context = factory.load(edgerc, section, account_key)
        
        if startDate is None:
            (startDate, endDate) = self.getPriorDayRange()

        url = self.buildUrlTrafficUrl(context, objectIds=objectIds, startDate=startDate, endDate=endDate)
        
        if debug:
            print(" ... Getting Url: {}".format(url), file=sys.stderr )

        result = context.session.get(url)
        code, json_obj = self.handleResponse(result, url, debug)

        if code in [200] and "data" in json_obj:


            for data in json_obj["data"]:
                self.convert_strings_to_numbers(data)

            enableDataTruncate = False
            if enableDataTruncate and len(json_obj["data"]) == 1:
                json_obj["data"] = json_obj["data"][0]

                if "objectIds" in json_obj:
                    del json_obj["objectIds"]

            if "metadata" in json_obj and "columns" in json_obj["metadata"]:
                del json_obj["metadata"]["columns"]
            
            if "metadata" in json_obj:
                availableDataEnds = json_obj["metadata"]["availableDataEnds"] 
                
                if availableDataEnds is not None:
                    date_time_obj = datetime.datetime.strptime(availableDataEnds, '%Y-%m-%dT%H:%M:%SZ')
                    endDate_Time = datetime.datetime.combine(endDate, datetime.time(0, 0))

                    if date_time_obj >= endDate_Time:
                        return (code, json_obj)
                    else:
                        return (code, json_obj)


            return (code, json_obj)
        else:
            return (code, json_obj)

    
