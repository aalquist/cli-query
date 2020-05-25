import requests
import json

def isAkamai(dnsName):
    if "type" in dnsName and dnsName["type"] == 5 and "data" in dnsName:
        data = dnsName["data"]
        akamaiDNSTupple = ("akamaiedge.net.", "edgekey.net.", "edgesuite.net.", "akamaized.net.", "akamai.net.", "akamaihd.net.")
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
    with requests.Session() as s:

        if recoredType is not None:
            response = s.get(f"https://dns.google.com/resolve?type={recoredType}&name={domain}")
        else:
            response = s.get(f"https://dns.google.com/resolve?name={domain}")

        dnsResponse = response.json()

        return dnsResponse

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
        return jsonDict

    jsonMap = list(map(mapDomainMeta , jsonMap ))

    return jsonMap

def checkDNSMetadata(domainList, recoredType="AAAA"):

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

if __name__ == "__main__":

    DNSInfo = checkDNSMetadata(["www.akamai.com", "www.alquist.nl", "www.google.com", "www-fake.alquist.nl"], recoredType=None )

    print( json.dumps(DNSInfo, indent=1) )
    


   