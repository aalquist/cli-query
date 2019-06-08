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

class NetStorageFetch(Fetch_Akamai_OPENAPI_Response):


    def fetchNetStorageGroups(self, *, edgerc, section, account_key, debug=False):

        factory = CredentialFactory()
        context = factory.load(edgerc, section, account_key)
        
        url = self.buildUrl("https://{}/storage/v1/storage-groups", context)
        
        result = context.session.get(url)
        code, json = self.handleResponse(result, url, debug)

        if code in [200] and "items" in json:
            json = json["items"]
            return (code, json)
        else:
            return (code, json)

    def fetchNetStorageUsers(self, *, edgerc, section, account_key, debug=False):

        factory = CredentialFactory()
        context = factory.load(edgerc, section, account_key)
        
        url = self.buildUrl("https://{}/storage/v1/upload-accounts", context)
        
        result = context.session.get(url)
        code, json = self.handleResponse(result, url, debug)

        if code in [200] and "items" in json:
            json = json["items"]
            return (code, json)
        else:
            return (code, json)
        
    