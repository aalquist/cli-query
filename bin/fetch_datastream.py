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

class DataStreamFetch(Fetch_Akamai_OPENAPI_Response):

    def formatDatetoString(self, dateobj):
        timeformat = "%Y-%m-%dT%H:%M:%SZ"
        return dateobj.strftime(timeformat)

    
    def createDatefromString(self, start):
        format = '%Y-%m-%dT%H:%M:%SZ'
        d = datetime.datetime.strptime(start, format)
        d.replace(tzinfo=pytz.UTC)
        return d
        

    def parseRange(self, start=None, timerange="2m"):
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

            if start is None:
                start = datetime.datetime.utcnow()

            elif not isinstance(start, datetime.date) :
                start = self.createDatefromString(start)

            end = start + delta
            
            return (self.formatDatetoString(start), self.formatDatetoString(end) )
            

    def buildStreamUrl(self, context, *, streamId=None, startTime=None, timerange=None):
        
        if streamId is None:
            raise ValueError("streamId is required")

        url = self.buildUrl("https://{}/datastream-pull-api/v1/streams/{}/raw-logs", context, streamId)

        if timerange is None and startTime is None:
            (startTime, endTime) = self.parseRange()
        
        elif timerange is None:
            (startTime, endTime) = self.parseRange(start=startTime)

        else:
            (startTime, endTime) = self.parseRange(start=startTime, timerange=timerange)

        queryArgs = [("start", startTime), ("end", endTime)]

        url = self.appendQueryStringTupple(url, queryArgs)
        return url

    def fetchLogs(self, *, edgerc, section, streamId=None, startTime=None, timeRange=None, debug=False):

        factory = CredentialFactory()
        context = factory.load(edgerc, section, None)
        
        url = self.buildStreamUrl(context, streamId=streamId, startTime=startTime, timerange=timeRange)
        
        result = context.session.get(url)
        code, json = self.handleResponse(result, url, debug)

        if code in [200] and "items" in json:
            json = json["items"]
            return (code, json)
        else:
            return (code, json)

    
        
    