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

import os
from akamai.edgegrid import EdgeGridAuth, EdgeRc
import requests
import configparser
import sys
import json
import time

from bin.credentialfactory import CredentialFactory

from bin.decorator import cacheFunctionCall

class Fetch_Akamai_OPENAPI_Response():

   

    def appendQueryStringTupple(self, url, tupleKeyPairArray = None):
        
        if( tupleKeyPairArray is None or len(tupleKeyPairArray) == 0):
            raise ValueError("tupleKeyPairArray not a list or None")

        for (key, value) in tupleKeyPairArray:
            
            if value is None:
                continue

            if '?' in url:
                url = "{}&{}={}".format(url,key,value)
            else:
                url = "{}?{}={}".format(url,key,value)

        return url

    def appendQueryStringArg(self, url, argKeySet):
        
        if '?' in url:
            url = "{}&{}".format(url,argKeySet)
        else:
            url = "{}?{}".format(url,argKeySet)

        return url

    def makeSwitchUrl(self, url, account_switch_key):
        
        url = self.appendQueryStringArg(url,account_switch_key)
        return url

    def buildUrl(self, url, context, *argv):

        url = url.format(context.base_url, *argv)
        
        if context.account_key != '' :
            url = self.makeSwitchUrl(url, context.account_key)

        return url

    def handleUnexpected(self, result, url, debug):
        if debug:
            _json = result.json()
            print(json.dumps(_json, indent=1 ), file=sys.stderr )
        
        raise Exception("Unexpected Reponse Code: {} for {}".format(result.status_code, url)  )
             
    
    def handleResponse(self, result, url, debug, retry = 0, context=None):

        status_code = result.status_code

        if status_code in [200, 201, 202]:
            _json = result.json()
            return (status_code, _json)
        
        elif status_code in [204]:
            return (status_code, dict() )

        elif status_code in [500, 501, 502, 503]:
            
            if retry > 0 and context is not None and result.request.method == "GET":
                
                print(" ... Encountered server error {} with {} retries remaining in 15 seconds".format(status_code, retry) , file=sys.stderr )

                if debug:
                    _json = result.json()
                    print(json.dumps(_json, indent=1 ), file=sys.stderr )

                time.sleep(15)

                result = context.session.get(url) 
                retry = retry - 1
                return self.handleResponse(result,url,debug, retry=retry, context=context)
                
            else: 
                self.handleUnexpected(result, url, debug)

        else: 
            self.handleUnexpected(result, url, debug)

    def handleResponseWithHeaders(self, result, url, debug, retry = 0, headers=None, context=None):

        status_code = result.status_code

        if status_code in [200, 202]:
            _json = result.json()
            _headers = result.headers
            return (status_code, _headers, _json)
        
        if status_code in [500, 501, 502, 503]:
            
            if retry > 0 and context is not None and result.request.method == "GET":
                time.sleep(15)

                print(" ... Encountered server error {} with {} retries remaining in 15 seconds".format(status_code, retry) , file=sys.stderr )

                if debug:
                    _json = result.json()
                    print(json.dumps(_json, indent=1 ), file=sys.stderr )

                time.sleep(15)
                retry = retry - 1

                if headers is not None:
                    result = context.session.get(url, headers=headers ) 
                    return self.handleResponseWithHeaders(result,url,debug, retry=retry, headers=headers, context=context)
                else:
                    result = context.session.get(url ) 
                    return self.handleResponseWithHeaders(result,url,debug, retry=retry, context=context)
            else: 
                self.handleUnexpected(result, url, debug)

        else: 
            self.handleUnexpected(result, url, debug)

class CachedContextHandler(Fetch_Akamai_OPENAPI_Response):

    def __init__(self, context, cache=None, debug=False):
        self.context = context
        self.debug = debug
        self.cache = cache
    
    def get(self, url, requestHeaders=None, bypassCache=False):

        if not bypassCache:
            value = cacheFunctionCall(self._get, self.cache, url, requestHeaders=requestHeaders)

        else:
            value = self._get(url, requestHeaders=requestHeaders)
        
        return value

    def _get(self, url, requestHeaders=None):
        result = self.context.session.get(url)
        return self.handleResponse(result, url, self.debug, retry=3, context=self.context)

    
    
