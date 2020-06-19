import requests
import json
import sys

typedict =  {
                "1": {
                    "type_name": "A"
                },
                "2": {
                    "type_name": "NS"
                },
                "3": {
                    "type_name": "MD"
                },
                "4": {
                    "type_name": "MF"
                },
                "5": {
                    "type_name": "CNAME"
                },
                "6": {
                    "type_name": "SOA"
                },
                "7": {
                    "type_name": "MB"
                },
                "8": {
                    "type_name": "MG"
                },
                "9": {
                    "type_name": "MR"
                },
                "10": {
                    "type_name": "NULL"
                },
                "11": {
                    "type_name": "WKS"
                },
                "12": {
                    "type_name": "PTR"
                },
                "13": {
                    "type_name": "HINFO"
                },
                "14": {
                    "type_name": "MINFO"
                },
                "15": {
                    "type_name": "MX"
                },
                "16": {
                    "type_name": "TXT"
                },
                "17": {
                    "type_name": "RP"
                },
                "18": {
                    "type_name": "AFSDB"
                },
                "19": {
                    "type_name": "X25"
                },
                "20": {
                    "type_name": "ISDN"
                },
                "21": {
                    "type_name": "RT"
                },
                "22": {
                    "type_name": "NSAP"
                },
                "23": {
                    "type_name": "NSAP-PTR"
                },
                "24": {
                    "type_name": "SIG"
                },
                "25": {
                    "type_name": "KEY"
                },
                "26": {
                    "type_name": "PX"
                },
                "27": {
                    "type_name": "GPOS"
                },
                "28": {
                    "type_name": "AAAA"
                },
                "29": {
                    "type_name": "LOC"
                },
                "30": {
                    "type_name": "NXT"
                },
                "31": {
                    "type_name": "EID"
                },
                "32": {
                    "type_name": "NIMLOC"
                },
                "33": {
                    "type_name": "SRV"
                },
                "34": {
                    "type_name": "ATMA"
                },
                "35": {
                    "type_name": "NAPTR"
                },
                "36": {
                    "type_name": "KX"
                },
                "37": {
                    "type_name": "CERT"
                },
                "38": {
                    "type_name": "A6"
                },
                "39": {
                    "type_name": "DNAME"
                },
                "40": {
                    "type_name": "SINK"
                },
                "41": {
                    "type_name": "OPT"
                },
                "42": {
                    "type_name": "APL"
                },
                "43": {
                    "type_name": "DS"
                },
                "44": {
                    "type_name": "SSHFP"
                },
                "45": {
                    "type_name": "IPSECKEY"
                },
                "46": {
                    "type_name": "RRSIG"
                },
                "47": {
                    "type_name": "NSEC"
                },
                "48": {
                    "type_name": "DNSKEY"
                },
                "49": {
                    "type_name": "DHCID"
                },
                "50": {
                    "type_name": "NSEC3"
                },
                "51": {
                    "type_name": "NSEC3PARAM"
                },
                "52": {
                    "type_name": "TLSA"
                },
                "53": {
                    "type_name": "SMIMEA"
                },
                "54": {
                    "type_name": "Unassigned"
                },
                "55": {
                    "type_name": "HIP"
                },
                "56": {
                    "type_name": "NINFO"
                },
                "57": {
                    "type_name": "RKEY"
                },
                "58": {
                    "type_name": "TALINK"
                },
                "59": {
                    "type_name": "CDS"
                },
                "60": {
                    "type_name": "CDNSKEY"
                },
                "61": {
                    "type_name": "OPENPGPKEY"
                },
                "62": {
                    "type_name": "CSYNC"
                },
                "63": {
                    "type_name": "ZONEMD"
                },
                "99": {
                    "type_name": "SPF"
                },
                "100": {
                    "type_name": "UINFO"
                },
                "101": {
                    "type_name": "UID"
                },
                "102": {
                    "type_name": "GID"
                },
                "103": {
                    "type_name": "UNSPEC"
                },
                "104": {
                    "type_name": "NID"
                },
                "105": {
                    "type_name": "L32"
                },
                "106": {
                    "type_name": "L64"
                },
                "107": {
                    "type_name": "LP"
                },
                "108": {
                    "type_name": "EUI48"
                },
                "109": {
                    "type_name": "EUI64"
                },
                "249": {
                    "type_name": "TKEY"
                },
                "250": {
                    "type_name": "TSIG"
                },
                "251": {
                    "type_name": "IXFR"
                },
                "252": {
                    "type_name": "AXFR"
                },
                "253": {
                    "type_name": "MAILB"
                },
                "254": {
                    "type_name": "MAILA"
                },
                "256": {
                    "type_name": "URI"
                },
                "257": {
                    "type_name": "CAA"
                },
                "258": {
                    "type_name": "AVC"
                },
                "259": {
                    "type_name": "DOA"
                },
                "260": {
                    "type_name": "AMTRELAY"
                }
            }

def lookupCode(code):
    code = str(code)
    if str(code) in typedict:
        typeName = typedict[code]['type_name']
        return typeName
    else:
        return None

def updateDNSAnswer(answer):
    
    if "type" in answer:
        codeName = lookupCode(answer["type"])
        answer["typeName"] = codeName
    
    return answer

def isAkamai(dnsName):
    if "type" in dnsName and dnsName["type"] == 5 and "data" in dnsName:
        data = dnsName["data"]
        akamaiDNSTupple = ("akamaiedge.net.", "akamaiedge-staging.net.", "edgekey.net.", "edgekey-staging.net.", "edgesuite.net.", "edgesuite-staging.net.", "akamaized.net.", "akamaized-staging.net.", "akamai.net.", "akamai-staging.net.", "akamaihd.net.", "akamaihd-staging.net.")
        hasAkamaiCNAME = data.endswith(akamaiDNSTupple)
        return hasAkamaiCNAME
    else:
        return False

def isIPV6(dnsName):
    if "type" in dnsName and dnsName["type"] == 28 and "data" in dnsName:
        return True
    else:
        return False

def getDomainJson(domain, recoredType="AAAA"):

    checkInvalidDNSChars(domain)

    s = requests.Session()

    if recoredType is not None:
        url = "https://dns.google.com/resolve?type={}&name={}".format(recoredType,domain)
        response = s.get(url)
        
    else:
        url = "https://dns.google.com/resolve?name={}".format(domain)
        response = s.get(url)

    dnsResponse = response.json()
    s.close()

    return dnsResponse

def markupTypeCodes(domainJson):
    
    dnsResponse = domainJson
    if "Answer" in dnsResponse and len(dnsResponse["Answer"])> 0:
        updatedList = list(map(lambda x : updateDNSAnswer(x), dnsResponse["Answer"] ) ) 
        dnsResponse["Answer"] = updatedList


def checkSingleDNSDomainJson(domainJson, func=None):
    
    dnsResponse = domainJson
    if "Answer" in dnsResponse and len(dnsResponse["Answer"])> 0:
        anyExists = any( list(map(lambda x : func(x), dnsResponse["Answer"] ) ) )
        return anyExists
    else:
        return (False, False)

def compositeCheck(domainList, recoredType="AAAA"):

    jsonMap = list(map(lambda domain : {"domain": domain, "dnsJson" : getDomainJson(domain, recoredType=recoredType) }, domainList ))

    def mapDomainMeta(jsonDict):
        jsonDict["isAkamai"] = checkSingleDNSDomainJson(jsonDict["dnsJson"], isAkamai)
        jsonDict["isIPV6"] = checkSingleDNSDomainJson(jsonDict["dnsJson"], isIPV6)
        
        markupTypeCodes(jsonDict["dnsJson"])

        return jsonDict

    jsonMap = list(map(mapDomainMeta , jsonMap ))

    return jsonMap

def checkInvalidDNSChars(dns):
    notAllowed = ["{", "}", "[", "]", ":" , ","]
    containsNotAllowed = [e for e in notAllowed if e in dns]

    if len(containsNotAllowed) > 0:
        raise ValueError("... domain {} has wrong char {}".format(dns, containsNotAllowed))


def checkJsonArrayDNS(jsonObj, arrayHostIndex=1, requireAnyAkamai=True, requireAllAkamai=False, returnAkamaiHosts=None):

    objList = list(map(lambda x : json.loads(x), jsonObj))

    returnList = list()

    for obj in objList:

        if arrayHostIndex >= len(obj):
            raise ValueError("index {} is >= size {}. choose a smaller number. line:\n{}".format(arrayHostIndex, len(obj) , obj))

        elif isinstance(obj, list):

            hostIndex = obj[arrayHostIndex]

            #check if input is a string, otherwise assume its a list
            if isinstance(hostIndex, str):
                hosts = hostIndex.split(",")
            else:
                hosts = hostIndex

            if len(obj) > 0: 
                print(" ... checking dns for {} hosts on {}".format( len(hosts), obj[0] ), file=sys.stderr )

            dnsResults = checkDNSMetadata(hosts)
        
        if requireAllAkamai:
            requireAnyAkamai = False
        
        if returnAkamaiHosts is not None :
            #modify the hostnames returned to only show the ones that are CNAMEd to Akamai or not
            returnToList = list(filter(lambda x : x["isAkamai"] == returnAkamaiHosts, dnsResults["resolution"]))

            returnedHostTypeText = "CNAMED" if returnAkamaiHosts else "Non-CNAMED"
           
            if len(hosts) != len(returnToList):
                print("  ... {} had {} hosts thet were reduced to {} {} hosts".format( obj[0], len(hosts), len(returnToList), returnedHostTypeText ), file=sys.stderr )
            else:
                print("  ... no hosts were filtered".format( len(hosts) ), file=sys.stderr )

            returnToList = list(map(lambda x : x["domain"], returnToList))
            
            if isinstance(hostIndex, str):
                returnToList = ",".join(returnToList)

            obj[arrayHostIndex] = returnToList

            if len(returnToList ) > 0:
                returnList.append(obj)

        else:

            if requireAnyAkamai == True and dnsResults["anyAkamai"] :
                returnList.append(obj)

            elif requireAllAkamai == True and dnsResults["allAkamai"] :
                returnList.append(obj)
            
            elif requireAnyAkamai == False and requireAnyAkamai == dnsResults["anyAkamai"] :
                returnList.append(obj)

    return returnList

def loadDNSfromHostList(domainList, recoredType="AAAA"):
    hostCheck = compositeCheck(domainList, recoredType=recoredType)

    isAkamai = list(map(lambda domain : domain["isAkamai"], hostCheck) )
    isIPV6 = list(map(lambda domain : domain["isIPV6"], hostCheck) )

    DNSInfo = {
        "anyAkamai" : any(isAkamai),
        "allAkamai" : all(isAkamai),
        "allIPv6" : all(isIPV6),
        "anyIPv6" : any(isIPV6),
        "resolution" : hostCheck
    }

    return DNSInfo

def checkDNSMetadata(inputList, inputIsJSON=False, recoredType="AAAA"):

    if inputIsJSON == False:
       return loadDNSfromHostList(inputList, recoredType="AAAA")

    else:
        return checkJsonArrayDNS(inputList, arrayHostIndex=1, requireAnyAkamai=True, requireAllAkamai=False, returnAkamaiHosts=None)

   