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
from bin.fetch_datastream import daysSince

from bin.decorator import cacheFunctionCall

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def logOKHeader(strOut, end=None):
    if end is None:
        print(f"{bcolors.HEADER}{strOut}{bcolors.ENDC}", file=sys.stderr)
    else:
        print(f"{bcolors.HEADER}{strOut}{bcolors.ENDC}", file=sys.stderr, end=end)

def logOKStatus(strOut, end=None):
    if end is None:
        print(f"{bcolors.OKGREEN}{strOut}{bcolors.ENDC}", file=sys.stderr)
    else:
        print(f"{bcolors.OKGREEN}{strOut}{bcolors.ENDC}", file=sys.stderr, end=end)

def logWarnStatus(strOut, end=None):
    if end is None:
        print(f"{bcolors.WARNING}{strOut}{bcolors.ENDC}", file=sys.stderr)
    else:
        print(f"{bcolors.WARNING}{strOut}{bcolors.ENDC}", file=sys.stderr, end=end)
        
def logFailStatus(strOut, end=None):
    if end is None:
        print(f"{bcolors.FAIL}{strOut}{bcolors.ENDC}", file=sys.stderr)
    else:
        print(f"{bcolors.FAIL}{strOut}{bcolors.ENDC}", file=sys.stderr, end=end)

def logStatus(strOut, end=None):
    if end is None:
        print(f"{bcolors.OKBLUE}{strOut}{bcolors.ENDC}", file=sys.stderr)
    else:
        print(f"{bcolors.OKBLUE}{strOut}{bcolors.ENDC}", file=sys.stderr, end=end)

def logFYI(strOut, end=None):
    if end is None:
        print(strOut, file=sys.stderr)
    else:
        print(strOut, file=sys.stderr, end=end)

class PropertyManagerFetch(Fetch_Akamai_OPENAPI_Response):

    forceTempCache = False

    @staticmethod
    def UseTempCache():
        PropertyManagerFetch.forceTempCache = True

    @staticmethod
    def DisableTempCache():
        PropertyManagerFetch.forceTempCache = False

    def __init__(self, tempCache=False):
        
        cacheDir = os.environ.get('AKAMAI_CLI_CACHE_PATH')
        cacheDirCommand = os.environ.get('AKAMAI_CLI_COMMAND')

        if PropertyManagerFetch.forceTempCache:
            self.cache = Cache()
            self.cache.clear()

        elif not tempCache and cacheDir is not None and cacheDirCommand is not None :
            self.cache = Cache(directory="{}/{}/PropertyManagerFetch".format(cacheDir,cacheDirCommand) )

        elif not tempCache:
            self.cache = Cache(directory="cache/PropertyManagerFetch")

        else:
            self.cache = Cache()
            self.cache.clear()
        

    def buildBulkSearchUrl(self, context, *, contractId=None, groupId=None):
        
        url = self.buildUrl("https://{}/papi/v1/bulk/rules-search-requests", context)

        queryArgs = [("contractId", contractId), ("groupdId", groupId)]

        url = self.appendQueryStringTupple(url, queryArgs)
        return url

    def buildGetPropertyUrl(self, context, *, propertyId=None, propertyVersion=None):
        
        uri = "/papi/v1/properties/{}/versions/{}/rules".format(propertyId,propertyVersion)
        url = self.buildUrl("https://{}" + uri, context)
        return url

    def buildGetPropertyDigitalPropertyUrl(self, context, *, propertyId=None, propertyVersion=None):
        
        #/papi/v1/properties/{propertyId}/versions/{propertyVersion}/hostnames{?contractId,groupId,validateHostnames}

        uri = "/papi/v1/properties/{}/versions/{}/hostnames".format(propertyId,propertyVersion)
        url = self.buildUrl("https://{}" + uri, context)

        queryArgs = [("validateHostnames", "false")]

        url = self.appendQueryStringTupple(url, queryArgs)

        
        return url

    def buildGetPropertyVersionMetaInfoUrl(self, context, *, propertyId=None, propertyVersion=None):

        #https://developer.akamai.com/api/core_features/property_manager/v1.html#api1580152614326

        uri = "/papi/v1/properties/{}/versions/{}".format(propertyId,propertyVersion)
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
            maxAttempts = 550

            while status != "COMPLETE" and attempts < maxAttempts:

                if status == "ERROR":
                    print(" ... Encountered error from bulksearch endpoint", file=sys.stderr )
                    print(" ... fatalError message from API response: {}".format(json["fatalError"]), file=sys.stderr )
                    print(" ... Error Bulksearch Request POST body:", file=sys.stderr )
                    print(" ... {}".format( jsonlib.dumps(postdata) ), file=sys.stderr )
                    

                    if debug:
                        print(" ... Error bulksearch POST JSON response:", file=sys.stderr )
                        print(" ... {}".format( jsonlib.dumps(json) ), file=sys.stderr )
                    
                    if "bulkSearchId" in json and "fatalError" in json:
                        raise ValueError("Error bulksearch API response bulkSearchId: \"{}\" fatalError message: \"{}\"".format(json["bulkSearchId"], json["fatalError"]))
                    else:
                        raise ValueError("Error bulksearch API response. Unknown error. No bulkSearchId and fatalError json keys")

                attempts = attempts + 1

                if attempts == 1:
                    time.sleep(3)

                result = context.session.get(locationURL )
                code, headers, json = self.handleResponseWithHeaders(result, url, debug, retry=1, context=context)
                status = json["searchTargetStatus"]

                if debug:
                    print(" ... Waiting for search results. {} attempt {} of {} for {}".format(status, attempts, maxAttempts, locationURL), file=sys.stderr )
                    print(" .... got HTTP code {} with headers: {}".format(code, jsonlib.dumps(dict(headers) ) ), file=sys.stderr)
                    print(" .... got json: {}".format(jsonlib.dumps(json) ), file=sys.stderr)
                else:
                    print(" ... Waiting for search results. {} attempt {} of {}".format(status, attempts, maxAttempts), file=sys.stderr )

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
        else:
            print(" ... Warning: searching non-cacheable properties. Limit to production or staging network for faster searching" , file=sys.stderr )
        
        if debug == True:
            print(" ... filtered json:", file=sys.stderr )
            printjson = jsonlib.dumps(json, indent=2)
            print(printjson, file=sys.stderr )

        

        def manipulateSearchResults(matchJson, edgerc=None, account_key=None, propertyId=None, propertyVersion=None, cacheResponses=False, debug=None):
            
            (code, propertyJson) = self.fetchPropertyVersion(edgerc=edgerc, propertyId=propertyId, propertyVersion=propertyVersion, account_key=account_key, cacheResponses=cacheResponses, debug=debug )

            if code in [200, 202]:
                self.mergeVersionPointerValues(matchJson, propertyJson)

                print(" ..... with hostnames, notes, formats, product_ids, etc..",  file=sys.stderr )
                (code, digitalPropertyJson) = self.fetchPropertyVersionDigitalProperty(edgerc=edgerc, account_key=account_key, propertyId=propertyId, propertyVersion=propertyVersion, cacheResponses=cacheResponses, debug=debug)

                if code in [200]:
                    lastModifiedTime = matchJson["lastModifiedTime"] if "lastModifiedTime" in matchJson else None
                    self.mergeDigitalPropertiesValues(matchJson, digitalPropertyJson, lastModifiedTime=lastModifiedTime)

                
                (code, versionMetaJson) = self.fetchPropertyVersionMetaInfo(edgerc=edgerc, account_key=account_key, propertyId=propertyId, propertyVersion=propertyVersion, cacheResponses=cacheResponses, debug=debug)

                if code in [200]:
                    self.mergeDigitalPropertiesVersionMeta(matchJson, versionMetaJson)

        originalLen = len(json)

        json = list( filter( lambda x : "propertyType" in x and x["propertyType"] == "TRADITIONAL", json  ) )
        jobsize = len(json)

        if originalLen > jobsize:
            countChange = originalLen - jobsize
            logWarnStatus(" ... {} non TRADITIONAL (includes) were filtered out".format(countChange ) )

        for match in json:
            count = count + 1
            propertyId = match["propertyId"]
            propertyVersion = match["propertyVersion"]
            propertyName = match["propertyName"]
            productionStatus = match["productionStatus"]
            stagingStatus = match["stagingStatus"]
            propertyType = match["propertyType"]

            if productionStatus in [ "ACTIVE", "DEACTIVATED" ] or stagingStatus in [ "ACTIVE", "DEACTIVATED" ]:

                cacheResponses = True
                logStatus(" ... Getting Immutable {} Property {} of {}. {} v{} production={} staging={}".format( propertyType, count, jobsize, propertyName,propertyVersion, productionStatus, stagingStatus) )
                manipulateSearchResults(match, edgerc=edgerc, account_key=account_key, propertyId=propertyId, propertyVersion=propertyVersion, cacheResponses=cacheResponses, debug=debug)

            else:    
                cacheResponses = False
                logWarnStatus(" ... Getting {} property {} of {}. {} v{} production={} staging={}".format( propertyType, count, jobsize, propertyName,propertyVersion, productionStatus, stagingStatus) )
                manipulateSearchResults(match, edgerc=edgerc, account_key=account_key, propertyId=propertyId, propertyVersion=propertyVersion, cacheResponses=cacheResponses, debug=debug)

        return json

    def mergeVersionPointerValues(self, match, propertyJson):

        matchLocations = match["matchLocations"]
        matchResults = []
        for pointer in matchLocations:
            subjson = self.resolvepointer(pointer, propertyJson)
            matchResults.append(subjson)
        
        if len(matchResults) > 0:
            match["matchLocationResults"] = matchResults

    def mergeDigitalPropertiesValues(self, searchJson, hostnameJson, lastModifiedTime=None):

        if len(hostnameJson) > 0:
            searchJson["hostnames"] = hostnameJson

        if lastModifiedTime is not None:

            days = daysSince(lastModifiedTime)
            searchJson["daysSinceModified"] = days

    def mergeDigitalPropertiesVersionMeta(self, searchJson, versionMetaJson):

        if len(versionMetaJson) > 0:
            if "propertyVersion" in  versionMetaJson:
                    del versionMetaJson["propertyVersion"]
                    
            if "stagingStatus" in  versionMetaJson:                     
                del versionMetaJson["stagingStatus"]

            if "productionStatus" in  versionMetaJson:    
                del versionMetaJson["productionStatus"]

            if "etag" in  versionMetaJson:       
                del versionMetaJson["etag"]

            if "updatedDate" in  versionMetaJson:          
                del versionMetaJson["updatedDate"]

            searchJson["versionInfo"] = versionMetaJson


    def validateResponse(self, jsonObj, account_key=None, propertyId=None, propertyVersion=None,):

        if propertyId != jsonObj["propertyId"]:
                raise ValueError("Unexpected API response! Expecting propertyId={} but got {}".format(propertyId, jsonObj["propertyId"] ))

        #doesn't support hyphenated account keys as the return back different values
        #elif account_key is not None and account_key not in jsonObj["accountId"]:
        #    raise ValueError("Unexpected API response! Expecting accountId={} but got {}.".format(account_key,jsonObj["accountId"] ))

        elif "propertyVersion" in jsonObj and propertyVersion != jsonObj["propertyVersion"]:
            raise ValueError("Unexpected API response! Expecting propertyVersion={} but got {}.".format(propertyVersion,jsonObj["propertyVersion"] ))   

        elif "versions" in jsonObj and "items" in jsonObj["versions"] and ( len(jsonObj["versions"]["items"]) == 1 ):
            versionItem = jsonObj["versions"]["items"][0]

            if "propertyVersion" in versionItem and propertyVersion != versionItem["propertyVersion"]:
                pass

            
        else: 
            pass


    def fetchPropertyVersionMetaInfo(self, edgerc=None, section=None, account_key=None, propertyId=None, propertyVersion=None, cacheResponses=False, debug=False):

        factory = CredentialFactory()
        context = factory.load(edgerc, section, account_key)
        url = self.buildGetPropertyVersionMetaInfoUrl(context, propertyId=propertyId, propertyVersion=propertyVersion)

        headers={"Content-Type": "application/json", "Accept": "application/json, */*"}
        bypassCache = not cacheResponses
        
        cachedHandler = CachedContextHandler(context, self.cache, debug=debug)
        code, jsonObj = cachedHandler.get(url, requestHeaders=headers, bypassCache=bypassCache)
        
        if code in [200] and "versions" in jsonObj and "items" in jsonObj["versions"]:
            self.validateResponse(jsonObj, account_key=account_key, propertyId=propertyId, propertyVersion=propertyVersion)
            jsonObj = jsonObj["versions"]["items"][0]

            return (code, jsonObj)
        else:
            return (code, jsonObj)    
        
    def fetchPropertyVersionDigitalProperty(self, edgerc=None, section=None, account_key=None, propertyId=None, propertyVersion=None, cacheResponses=False, debug=False):

        factory = CredentialFactory()
        context = factory.load(edgerc, section, account_key)
        url = self.buildGetPropertyDigitalPropertyUrl(context, propertyId=propertyId, propertyVersion=propertyVersion)

        headers={"Content-Type": "application/json", "Accept": "application/json, */*"}
        bypassCache = not cacheResponses
        
        cachedHandler = CachedContextHandler(context, self.cache, debug=debug)
        code, jsonObj = cachedHandler.get(url, requestHeaders=headers, bypassCache=bypassCache)
        
        if code in [200] and "hostnames" in jsonObj and "items" in jsonObj["hostnames"]:
            self.validateResponse(jsonObj, account_key=account_key, propertyId=propertyId, propertyVersion=propertyVersion)
            jsonObj = jsonObj["hostnames"]["items"]

            return (code, jsonObj)
        else:
            return (code, jsonObj)        

    
    def fetchPropertyVersion(self, edgerc=None, section=None, account_key=None, propertyId=None, propertyVersion=None, cacheResponses=False, debug=False):

        factory = CredentialFactory()
        context = factory.load(edgerc, section, account_key)
        url = self.buildGetPropertyUrl(context, propertyId=propertyId, propertyVersion=propertyVersion)

        headers={"Content-Type": "application/json", "Accept": "application/json, */*"}
        bypassCache = not cacheResponses
        cachedHandler = CachedContextHandler(context, self.cache, debug=debug)
        code, jsonObj = cachedHandler.get(url, requestHeaders=headers, bypassCache=bypassCache)
        
        if code in [200, 201, 202] and "rules" in jsonObj:

            self.validateResponse(jsonObj, account_key=account_key, propertyId=propertyId, propertyVersion=propertyVersion)
            return (code, jsonObj)
            
        else:
            return (code, jsonObj)

    
    def resolvepointer(self, pointer, doc):
        doc = copy.deepcopy(doc)
        pointerJson = jsonpointer.resolve_pointer(doc, pointer)
        return pointerJson
