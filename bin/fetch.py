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

from bin.credentialfactory import CredentialFactory

class Fetch_Akamai_OPENAPI_Response():

    def makeSwitchUrl(self, url, account_switch_key):
        
        if '?' in url:
            url = "{}&{}".format(url,account_switch_key)
        else:
            url = "{}?{}".format(url,account_switch_key)

        return url

    def buildUrl(self, url, context, *argv):
        url = url.format(context.base_url, *argv)
        
        if context.account_key != '' :
            url = self.makeSwitchUrl(url, context.account_key)

        return url

    def handleUnexpected(self, result, url, debug):
        if debug:
            lds_json = result.json()
            print(json.dumps(lds_json, indent=4 ), file=sys.stderr )
        
        raise Exception("Unexpected Reponse Code: {} for {}".format(result.status_code, url)  )
             
    
    def handleResponse(self, result, url, debug):

        status_code = result.status_code

        if status_code in [200]:
            lds_json = result.json()
            return (status_code, lds_json)
        
        else: 
            self.handleUnexpected(result, url, debug)