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
import re

from akamai.edgegrid import EdgeGridAuth, EdgeRc

from bin.credentialfactory import CredentialFactory
from bin.fetch import Fetch_Akamai_OPENAPI_Response

class LdsFetch(Fetch_Akamai_OPENAPI_Response):

    def parseCPCODENameForCodeOnly(self, name):

        regexFound = re.search(r'^(\d+)\s.*', name, flags=0)

        if regexFound is not None:
            group = regexFound.group(1)
            return group
        else:
            return None

    def adjustResponseJSON(self, json):

        for j in json:
            if "logSource" in j and "cpCode" in j["logSource"] :
                cpCodeNumber = self.parseCPCODENameForCodeOnly(j["logSource"]["cpCode"])
                j["logSource"]["cpCodeNumber"] = cpCodeNumber
        
        return json

    def fetchCPCodeProducts(self, *, edgerc, section, account_key, debug=False):

        factory = CredentialFactory()
        context = factory.load(edgerc, section, account_key)
        
        url = self.buildUrl("https://{}/lds-api/v3/log-sources/cpcode-products/log-configurations", context)
        
        result = context.session.get(url)

        code, json = self.handleResponse(result, url, debug)
        json = self.adjustResponseJSON(json)
        
        return (code, json)
        

    