
#http --timeout=600 --auth-type edgegrid -a default: GET :/papi/v1/groups accountSwitchKey==ACCOUNT_ID
#http --timeout=600 --auth-type edgegrid -a default: GET :/papi/v1/cpcodes contractId==ctr_P-2DY1VIU groupId==grp_144276 accountSwitchKey==ACCOUNT_ID

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

import sys

from akamai.edgegrid import EdgeGridAuth, EdgeRc

from bin.credentialfactory import CredentialFactory
from bin.fetch import Fetch_Akamai_OPENAPI_Response

class CPCODEFetch(Fetch_Akamai_OPENAPI_Response):

 
    def fetchGroupCPCODES(self, *, edgerc, section, account_key, debug=False):

        factory = CredentialFactory()
        context = factory.load(edgerc, section, account_key)
        
        url = self.buildUrl("https://{}/papi/v1/groups", context)
        
        result = context.session.get(url)
        code, json = self.handleResponse(result, url, debug)

        if code in [200] and "groups" in json:

            json = json["groups"]["items"]
            jobsize = len(json)
            returnList = []

            count=1
            for j in json:

                returnList.append( self.getGroupCPCODES(j, context, jobsize, count, debug) )
                count=count+1


            return (code, returnList)
        else:
            return (code, json)

    def getGroupCPCODES(self, item, context, jobsize, count, debug):
        
        if len( item["contractIds"]) > 0 :
            contractId = item["contractIds"][0]
            groupId = item["groupId"]


        url = self.buildUrl("https://{}/papi/v1/cpcodes?contractId={}&groupId={}", context, contractId, groupId)

        print(" ... {} of {} getting {} cpcodes".format( count, jobsize, groupId), file=sys.stderr )

        result = context.session.get(url)
        code, json = self.handleResponse(result, url, debug)

        if contractId != json["contractId"] or groupId != json["groupId"]:
            raise Exception("unexpected result! expecting contractId={} but got {}. Expecting groupId={} but got {}".format(contractId,json["contractId"],groupId, json["groupId"] ))

        result = []

        if code in [200] and "cpcodes" in json and "items" in json["cpcodes"]:

            cpcodesjson = json["cpcodes"]["items"]
            for jcode in cpcodesjson:

                cpcode = {}
                for key in jcode.keys():
                    cpcode[key] = jcode[key]
                    
                result.append(cpcode)
            
        item["cpcodes"] = result
        return item
        
    