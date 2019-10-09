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

import jsonpointer
import copy
import sys
import time
import json as jsonlib
import os

import functools
from functools import partial
from diskcache import Cache

from akamai.edgegrid import EdgeGridAuth, EdgeRc

from bin.credentialfactory import CredentialFactory
from bin.fetch import Fetch_Akamai_OPENAPI_Response
from bin.fetch import CachedContextHandler

from bin.decorator import cacheFunctionCall

class PropertyManagerFetch(Fetch_Akamai_OPENAPI_Response):

    def __init__(self):
        
        cacheDir = os.environ.get('AKAMAI_CLI_CACHE_PATH')
        cacheDirCommand = os.environ.get('AKAMAI_CLI_COMMAND')
        

        if cacheDir is not None and cacheDirCommand is not None :
            self.cache = Cache(directory="{}/{}/PropertyManagerFetch".format(cacheDir,cacheDirCommand) )
        else:
            self.cache = Cache(directory="cache/PropertyManagerFetch")
        

    def buildBulkSearchUrl(self, context, *, contractId=None, groupId=None):
        
        url = self.buildUrl("https://{}/papi/v1/bulk/rules-search-requests", context)

        queryArgs = [("contractId", contractId), ("groupdId", groupId)]

        url = self.appendQueryStringTupple(url, queryArgs)
        return url

    def buildGetPropertyUrl(self, context, *, propertyId=None, propertyVersion=None):
        
        uri = "/papi/v1/properties/{}/versions/{}/rules".format(propertyId,propertyVersion)
        url = self.buildUrl("https://{}" + uri, context)
        return url

    def bulksearch(self, edgerc=None, section=None, account_key=None, contractId=None, groupId=None, postdata=None, network=None, debug=False):

        factory = CredentialFactory()
        context = factory.load(edgerc, section, account_key)
        url = self.buildBulkSearchUrl(context, contractId=contractId, groupId=groupId)

        headers={"Content-Type": "application/json", "Accept": "application/json, */*"}

        result = context.session.post(url, json=postdata, headers=headers )
        code, headers, json = self.handleResponseWithHeaders(result, url, debug)

        if code in [200] and "results" in json:
            
            print(" ... Found {} properties".format( len(json["results"])) , file=sys.stderr )
        
            json = self.getMatchLocationValues(json["results"], edgerc=edgerc, account_key=account_key, network=network, debug=debug)
            return (code, json)
        
        elif code in [202]:

            locationURL = headers["Location"]
            result = context.session.get(locationURL )
            code, headers, json = self.handleResponseWithHeaders(result, url, debug)
            status = json["searchTargetStatus"]

            attempts = 0
            while status != "COMPLETE" and attempts < 550:

                if status == "ERROR":
                    print(" ... Encountered error from bulksearch endpoint", file=sys.stderr )
                    print(" ... fatalError message: {}".format(json["fatalError"]), file=sys.stderr )
                    print(" ... Review your search post for possible errors:", file=sys.stderr )
                    
                    postJSON = jsonlib.dumps(postdata)
                    print(postJSON, file=sys.stderr )
                    
                    raise ValueError("fatal bulk search error: {}".format(json["fatalError"]))

                attempts = attempts + 1

                if attempts == 1:
                    time.sleep(3)

                result = context.session.get(locationURL )
                code, headers, json = self.handleResponseWithHeaders(result, url, debug, retry=1, context=context)
                status = json["searchTargetStatus"]
                print(" ... Waiting for search results. {}".format(status), file=sys.stderr )

                if status != "COMPLETE":
                    time.sleep(7)

            print(" ... Found {} properties".format( len(json["results"])) , file=sys.stderr )
        
            if status == "COMPLETE":
                json = self.getMatchLocationValues(json["results"], edgerc=edgerc, account_key=account_key, network=network, debug=debug)
            else:
                raise ValueError("Search status never encountred COMPLETE. Last Status = {}".format(status))

            return (code, json)

        else:
            return (code, json)

    def getMatchLocationValues(self, json, edgerc=None, account_key=None, network=None, debug=False):
           
        count = 0 

        if network is not None and ( network.startswith("p") or network.startswith("P") ) :
            json = list(filter(lambda x: x["productionStatus"] == "ACTIVE", json) )
            print(" ... Limiting to production network with {} ACTIVE properties".format( len(json)) , file=sys.stderr )
        elif network is not None and ( network.startswith("s") or network.startswith("S") ) :
            json = list(filter(lambda x: x["stagingStatus"] == "ACTIVE", json) )
            print(" ... Limiting to staging network with {} ACTIVE properties".format( len(json)) , file=sys.stderr )
        if debug == True:
            print(" ... filtered json:", file=sys.stderr )
            printjson = jsonlib.dumps(json)
            print(printjson, file=sys.stderr )

        jobsize = len(json)

        for match in json:
            count = count + 1
            propertyId = match["propertyId"]
            propertyVersion = match["propertyVersion"]
            propertyName = match["propertyName"]
            productionStatus = match["productionStatus"]
            stagingStatus = match["stagingStatus"]

            if productionStatus in [ "ACTIVE", "DEACTIVATED" ] or stagingStatus in [ "ACTIVE", "DEACTIVATED" ]:
                print(" ... Getting Immutable Property {} of {}. {} v{} production={} staging={}".format( count, jobsize, propertyName,propertyVersion, productionStatus, stagingStatus), file=sys.stderr )
                (_, propertyJson) = self.fetchPropertyVersion(edgerc=edgerc, propertyId=propertyId, propertyVersion=propertyVersion, account_key=account_key, cacheResponses=True, debug=debug )

            else:    
                print(" ... Getting property {} of {}. {} v{} production={} staging={}".format( count, jobsize, propertyName,propertyVersion, productionStatus, stagingStatus), file=sys.stderr )
                (_, propertyJson) = self.fetchPropertyVersion(edgerc=edgerc, propertyId=propertyId, propertyVersion=propertyVersion, account_key=account_key, cacheResponses=False, debug=debug )


            

            matchLocations = match["matchLocations"]
            matchResults = []
            for pointer in matchLocations:
                subjson = self.resolvepointer(pointer, propertyJson)
                matchResults.append(subjson)
            
            if len(matchResults) > 0:
                match["matchLocationResults"] = matchResults

        return json

   
        
        

    
    def fetchPropertyVersion(self, edgerc=None, section=None, account_key=None, propertyId=None, propertyVersion=None, cacheResponses=False, debug=False):

        factory = CredentialFactory()
        context = factory.load(edgerc, section, account_key)
        url = self.buildGetPropertyUrl(context, propertyId=propertyId, propertyVersion=propertyVersion)

        headers={"Content-Type": "application/json", "Accept": "application/json, */*"}
        cachedHandler = CachedContextHandler(context, self.cache, cacheResponses=cacheResponses)
        code, json = cachedHandler.get(url, headers=headers)
        
        if code in [200, 201, 202] and "rules" in json:

            if propertyId != json["propertyId"]:
                raise ValueError("Unexpected API response! Expecting propertyId={} but got {}".format(propertyId, json["propertyId"] ))

            elif account_key is not None and account_key not in json["accountId"]:
                raise ValueError("Unexpected API response! Expecting accountId={} but got {}.".format(account_key,json["accountId"] ))

            elif propertyVersion != json["propertyVersion"]:
                raise ValueError("Unexpected API response! Expecting propertyVersion={} but got {}.".format(propertyVersion,json["propertyVersion"] ))

            return (code, json)
        else:
            return (code, json)

    
    def resolvepointer(self, pointer, doc):
        doc = copy.deepcopy(doc)
        pointerJson = jsonpointer.resolve_pointer(doc, pointer)
        return pointerJson
