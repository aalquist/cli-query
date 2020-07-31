import requests
import json
import sys

class Fetch_DNS():

    def __init__(self):
        s = requests.Session()
        s.mount('https://', requests.adapters.HTTPAdapter(pool_connections=2, pool_maxsize=4))
        self.http_Session = s
        s.headers = {}
    
    def __del__(self):
        if self.http_Session is not None:
            self.http_Session.close()


    typedict =  {"1":{"type_name":"A"},"2":{"type_name":"NS"},"3":{"type_name":"MD"},"4":{"type_name":"MF"},"5":{"type_name":"CNAME"},"6":{"type_name":"SOA"},"7":{"type_name":"MB"},"8":{"type_name":"MG"},"9":{"type_name":"MR"},"10":{"type_name":"NULL"},"11":{"type_name":"WKS"},"12":{"type_name":"PTR"},"13":{"type_name":"HINFO"},"14":{"type_name":"MINFO"},"15":{"type_name":"MX"},"16":{"type_name":"TXT"},"17":{"type_name":"RP"},"18":{"type_name":"AFSDB"},"19":{"type_name":"X25"},"20":{"type_name":"ISDN"},"21":{"type_name":"RT"},"22":{"type_name":"NSAP"},"23":{"type_name":"NSAP-PTR"},"24":{"type_name":"SIG"},"25":{"type_name":"KEY"},"26":{"type_name":"PX"},"27":{"type_name":"GPOS"},"28":{"type_name":"AAAA"},"29":{"type_name":"LOC"},"30":{"type_name":"NXT"},"31":{"type_name":"EID"},"32":{"type_name":"NIMLOC"},"33":{"type_name":"SRV"},"34":{"type_name":"ATMA"},"35":{"type_name":"NAPTR"},"36":{"type_name":"KX"},"37":{"type_name":"CERT"},"38":{"type_name":"A6"},"39":{"type_name":"DNAME"},"40":{"type_name":"SINK"},"41":{"type_name":"OPT"},"42":{"type_name":"APL"},"43":{"type_name":"DS"},"44":{"type_name":"SSHFP"},"45":{"type_name":"IPSECKEY"},"46":{"type_name":"RRSIG"},"47":{"type_name":"NSEC"},"48":{"type_name":"DNSKEY"},"49":{"type_name":"DHCID"},"50":{"type_name":"NSEC3"},"51":{"type_name":"NSEC3PARAM"},"52":{"type_name":"TLSA"},"53":{"type_name":"SMIMEA"},"54":{"type_name":"Unassigned"},"55":{"type_name":"HIP"},"56":{"type_name":"NINFO"},"57":{"type_name":"RKEY"},"58":{"type_name":"TALINK"},"59":{"type_name":"CDS"},"60":{"type_name":"CDNSKEY"},"61":{"type_name":"OPENPGPKEY"},"62":{"type_name":"CSYNC"},"63":{"type_name":"ZONEMD"},"99":{"type_name":"SPF"},"100":{"type_name":"UINFO"},"101":{"type_name":"UID"},"102":{"type_name":"GID"},"103":{"type_name":"UNSPEC"},"104":{"type_name":"NID"},"105":{"type_name":"L32"},"106":{"type_name":"L64"},"107":{"type_name":"LP"},"108":{"type_name":"EUI48"},"109":{"type_name":"EUI64"},"249":{"type_name":"TKEY"},"250":{"type_name":"TSIG"},"251":{"type_name":"IXFR"},"252":{"type_name":"AXFR"},"253":{"type_name":"MAILB"},"254":{"type_name":"MAILA"},"256":{"type_name":"URI"},"257":{"type_name":"CAA"},"258":{"type_name":"AVC"},"259":{"type_name":"DOA"},"260":{"type_name":"AMTRELAY"}}

    def lookupCode(self, code):
        code = str(code)
        if str(code) in self.typedict:
            typeName = self.typedict[code]['type_name']
            return typeName
        else:
            return None

    def updateDNSAnswer(self, answer):
        
        if "type" in answer:
            codeName = self.lookupCode(answer["type"])
            answer["typeName"] = codeName
        
        return answer

    def isAkamai(self, dnsName):
        if "type" in dnsName and dnsName["type"] == 5 and "data" in dnsName:
            data = dnsName["data"]
            akamaiDNSTupple = ("akamaiedge.net.", "akamaiedge-staging.net.", "edgekey.net.", "edgekey-staging.net.", "edgesuite.net.", "edgesuite-staging.net.", "akamaized.net.", "akamaized-staging.net.", "akamai.net.", "akamai-staging.net.", "akamaihd.net.", "akamaihd-staging.net.")
            hasAkamaiCNAME = data.endswith(akamaiDNSTupple)
            return hasAkamaiCNAME
        else:
            return False

    def isIPV6(self, dnsName):
        if "type" in dnsName and dnsName["type"] == 28 and "data" in dnsName:
            return True
        else:
            return False

    def getDomainJson(self, domain, recoredType=None, debug=False, progressTickHandler=None):

        self.checkInvalidDNSChars(domain)

        s = self.http_Session

        if recoredType is not None:
            url = "https://dns.google.com/resolve?type={}&name={}".format(recoredType,domain)
            response = s.get(url)
            
        else:
            url = "https://dns.google.com/resolve?name={}".format(domain)
            response = s.get(url)

        dnsResponse = response.json()

        if progressTickHandler is not None:
            progressTickHandler()
        
        if debug:
            print(json.dumps( dnsResponse, indent=1), file=sys.stderr )

        

        return dnsResponse

    def markupTypeCodes(self, domainJson):
        
        dnsResponse = domainJson
        if self.answerFound(dnsResponse):
            updatedList = list(map(lambda x : self.updateDNSAnswer(x), dnsResponse["Answer"] ) ) 
            dnsResponse["Answer"] = updatedList

    def answerFound(self, dnsResponse):
        answer ="Answer" in dnsResponse and len(dnsResponse["Answer"])> 0
        return answer

    def checkSingleDNSDomainJson(self, domainJson, func=None):
        
        dnsResponse = domainJson
        if self.answerFound(dnsResponse):
            anyExists = any( list(map(lambda x : func(x), dnsResponse["Answer"] ) ) )
            return anyExists
        else:
            return False

    def compositeCheck(self, domainList, recoredType=None, progressTickHandler=None, debug=False):

        jsonMap = list(map(lambda domain : {"domain": domain, "dnsJson" : self.getDomainJson(domain, recoredType=recoredType, progressTickHandler=progressTickHandler, debug=debug) }, domainList ))

        def mapDomainMeta(jsonDict):
            jsonDict["isAkamai"] = self.checkSingleDNSDomainJson(jsonDict["dnsJson"], self.isAkamai)
            #jsonDict["isIPV6"] = self.checkSingleDNSDomainJson(jsonDict["dnsJson"], self.isIPV6)
            jsonDict["NXDomain"] = not self.answerFound(jsonDict["dnsJson"])
            
            self.markupTypeCodes(jsonDict["dnsJson"])

            return jsonDict

        jsonMap = list(map(mapDomainMeta , jsonMap ))

        return jsonMap

    def checkInvalidDNSChars(self, dns):
        notAllowed = ["{", "}", "[", "]", ":" , ","]
        containsNotAllowed = [e for e in notAllowed if e in dns]

        if len(containsNotAllowed) > 0:
            raise ValueError("... domain {} has wrong char {}".format(dns, containsNotAllowed))
    
    def filterHosts(self, dnsResults, filterText="isAkamai", checkResultTrue=True):
        returnToList = list(filter(lambda x : x[filterText] == checkResultTrue , dnsResults["resolution"]))
        return returnToList

    def filterDNSInput(self, jsonObj, func, arrayHostIndex=1, progressTickHandler=None, debug=False):

        returnList = list()
        objList = list(map(lambda x : json.loads(x), jsonObj))

        for obj in objList:

            if arrayHostIndex >= len(obj):
                raise ValueError("index {} is >= size {}. choose a smaller number. line:\n{}".format(arrayHostIndex, len(obj) , obj))

            if len(obj) < 2:
                pass

            elif isinstance(obj, list):

                hostIndex = obj[arrayHostIndex]

                #check if input is a string, otherwise assume its a list
                if isinstance(hostIndex, str):
                    hosts = hostIndex.split(",")
                else:
                    hosts = hostIndex

                if len(obj) > 0: 
                    print(" ... checking dns for {} hosts on {}".format( len(hosts), obj[0] ), file=sys.stderr )

                originalHostLength = len(hosts)
                hosts = list(filter(lambda domain : "." in domain, hosts) )

                if len(hosts) < 1:
                    print("  ... no domains were valid so skipping".format( len(hosts) ), file=sys.stderr )    
                    continue

                elif len(hosts) != originalHostLength:
                    print("  ... some domains were not valid so skipped them".format( len(hosts) ), file=sys.stderr )    
        
                if progressTickHandler is not None:
                    print("  ...", end="", file=sys.stderr)
                func(obj, hosts, hostIndex, returnList, arrayHostIndex=arrayHostIndex, progressTickHandler=progressTickHandler, debug=debug)
                
                

        return returnList

    def hostsNotCNAMED(self, obj, hosts, hostIndex, returnList, arrayHostIndex=1, progressTickHandler=None, debug=False):
        
        dnsResults = self.loadDNSfromHostList(hosts, progressTickHandler=progressTickHandler, debug=debug)
        returnToList = self.filterHosts(dnsResults, filterText="isAkamai", checkResultTrue=False)
        
        if len(hosts) != len(returnToList) and len(returnToList) == 0:
            print("  ... {} had {} hosts and none were filtered".format( obj[0], len(hosts) ), file=sys.stderr )

        elif len(hosts) != len(returnToList):
            returnedHostTypeText = "Non-CNAMED"
            print("  ... {} had {} hosts which were reduced to {} {} hosts".format( obj[0], len(hosts), len(returnToList), returnedHostTypeText ), file=sys.stderr )
            self.printNXDomainErrMsg(dnsResults)

        else:
            print("  ... no hosts were filtered".format( len(hosts) ), file=sys.stderr )

        returnToList = list(map(lambda x : x["domain"], returnToList))
        
        if isinstance(hostIndex, str):
            returnToList = ",".join(returnToList)

        obj[arrayHostIndex] = returnToList

        if len(returnToList ) > 0:
            returnList.append(obj)
    
    def hostsCNAMED(self, obj, hosts, hostIndex, returnList, arrayHostIndex=1, progressTickHandler=None, debug=False):
        
        dnsResults = self.loadDNSfromHostList(hosts, progressTickHandler=progressTickHandler, debug=debug)
        returnToList = self.filterHosts(dnsResults, filterText="isAkamai", checkResultTrue=True)
        
        if len(hosts) != len(returnToList) and len(returnToList) == 0:
            print("  ... {} had {} hosts and none were filtered".format( obj[0], len(hosts) ), file=sys.stderr )

        elif len(hosts) != len(returnToList):
            returnedHostTypeText = "CNAMED"
            print("  ... {} had {} hosts which were reduced to {} {} hosts".format( obj[0], len(hosts), len(returnToList), returnedHostTypeText ), file=sys.stderr )
            self.printNXDomainErrMsg(dnsResults)

        else:
            print("  ... no hosts were filtered".format( len(hosts) ), file=sys.stderr )

        returnToList = list(map(lambda x : x["domain"], returnToList))
        
        if isinstance(hostIndex, str):
            returnToList = ",".join(returnToList)

        obj[arrayHostIndex] = returnToList

        if len(returnToList ) > 0:
            returnList.append(obj)

    def configsWithCNAME(self, obj, hosts, hostIndex, returnList, arrayHostIndex=1, progressTickHandler=None, debug=False):

        dnsResults = self.loadDNSfromHostList(hosts, progressTickHandler=progressTickHandler, debug=debug)
        returnToList = self.filterHosts(dnsResults, filterText="isAkamai" )
        
        self.printFilterStatusMsg(obj,hosts,returnToList,filterTypeName="CNAME")
        self.printNXDomainErrMsg(dnsResults)

        if dnsResults["anyAkamai"] :    
            returnList.append(obj)

    def configsFullyCNAME(self, obj, hosts, hostIndex, returnList, arrayHostIndex=1, progressTickHandler=None, debug=False):

        dnsResults = self.loadDNSfromHostList(hosts, progressTickHandler=progressTickHandler, debug=debug)
        returnToList = self.filterHosts(dnsResults, filterText="isAkamai" )

        self.printFilterStatusMsg(obj,hosts,returnToList,filterTypeName="CNAME")
        self.printNXDomainErrMsg(dnsResults)

        if dnsResults["allAkamai"] :    
            returnList.append(obj)

    def configsWithoutCNAME(self, obj, hosts, hostIndex, returnList, arrayHostIndex=1, progressTickHandler=None, debug=False):

        dnsResults = self.loadDNSfromHostList(hosts, progressTickHandler=progressTickHandler, debug=debug)
        returnToList = self.filterHosts(dnsResults, filterText="isAkamai", checkResultTrue=False )
        
        self.printFilterStatusMsg(obj,hosts,returnToList,filterTypeName="non-CNAME")
        self.printNXDomainErrMsg(dnsResults)

        if False == dnsResults["anyAkamai"] :    
            returnList.append(obj)
    
    def configsAllNXDomain(self, obj, hosts, hostIndex, returnList, arrayHostIndex=1, progressTickHandler=None, debug=False):

        filterText="NXDomain"
        dnsResults = self.loadDNSfromHostList(hosts, progressTickHandler=progressTickHandler, debug=debug)
        returnToList = self.filterHosts(dnsResults, filterText=filterText)
        
        self.printFilterStatusMsg(obj,hosts,returnToList,filterTypeName=filterText)

        if dnsResults["allNXDomain"] :    
            returnList.append(obj)

    def configsAnyNXDomain(self, obj, hosts, hostIndex, returnList, arrayHostIndex=1, progressTickHandler=None, debug=False):

        filterText="NXDomain"
        dnsResults = self.loadDNSfromHostList(hosts, progressTickHandler=progressTickHandler, debug=debug)

        if progressTickHandler is not None:
            print(" done", file=sys.stderr)
            
        returnToList = self.filterHosts(dnsResults, filterText=filterText)
        
        self.printFilterStatusMsg(obj,hosts,returnToList,filterTypeName=filterText)

        if dnsResults["anyNXDomain"] :    
            returnList.append(obj)

    def printFilterStatusMsg(self, obj, hosts, returnToList, filterTypeName=None):

        if filterTypeName is None:
            filterTypeName = ""
        else:
            filterTypeName = " {} ".format(filterTypeName)

        if len(hosts) == 1:
            print("  ... {} had {} host and was already a{}".format( obj[0], len(hosts), filterTypeName ), file=sys.stderr )
        else:
            print("  ... {} had {} hosts and filtered {}{}hosts".format( obj[0], len(hosts), len(returnToList),filterTypeName ), file=sys.stderr )


    def printNXDomainErrMsg(self, dnsResults):
        NXDomainList = list(filter(lambda x : x["NXDomain"] == True, dnsResults["resolution"]))
        NXDomainList = list(map(lambda x : x["domain"], NXDomainList))
        NXDomainListCount = len(NXDomainList)

        if NXDomainListCount > 0:
            if NXDomainListCount > 3:
                NXDomainList = NXDomainList[0:3]

            hostsText = "host" if NXDomainListCount == 1 else "hosts"
            truncatedHostsText = "Truncated NXDomain list" if NXDomainListCount > 3 else "NXDomain list"
            truncatedHostsTrainingText = " ... more" if NXDomainListCount > 3 else ""

            if NXDomainListCount == 1:
                print("   ... {} {} was NXDomain {} {}".format(NXDomainListCount, hostsText, NXDomainList, truncatedHostsTrainingText), file=sys.stderr )
            else:
                print("   ... {} {} were NXDomain {} {}".format(NXDomainListCount, hostsText, NXDomainList, truncatedHostsTrainingText), file=sys.stderr )


    def loadDNSfromHostList(self, domainList, recoredType=None, progressTickHandler=None, debug=False):
        hostCheck = self.compositeCheck(domainList, recoredType=recoredType, progressTickHandler=progressTickHandler, debug=debug)

        isAkamai = list(map(lambda domain : domain["isAkamai"], hostCheck) )
        #isIPV6 = list(map(lambda domain : domain["isIPV6"], hostCheck) )
        NXDomain = list(map(lambda domain : domain["NXDomain"], hostCheck) )

        DNSInfo = {
            "anyAkamai" : any(isAkamai),
            "allAkamai" : all(isAkamai),
            #"allIPv6" : all(isIPV6),
            #"anyIPv6" : any(isIPV6),
            "anyNXDomain" : any(NXDomain),
            "allNXDomain" : all(NXDomain),
            "resolution" : hostCheck
        }

        if progressTickHandler is not None:
            print(" done", file=sys.stderr)

        return DNSInfo

