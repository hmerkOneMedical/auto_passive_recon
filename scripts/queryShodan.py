import shodan
import os
import json

from helpers import *

SHODAN_API_KEY = os.environ['SHODAN_API_KEY']
api = shodan.Shodan(SHODAN_API_KEY)

def getDomainVulnerabilites(subdomains):
    ips = list(domainsToIPs(subdomains))
    ipResults = {}
    for ip in ips:
        try:
            res = ((api.host(ip)))
            ipResults[ip] = res['vulns']
        except:
            pass

    return ipResults


def findVulnerabilitiesWithIp(ip):
    try:
        result = api.host(ip)
        respSet = set([])
        for i in range(0, len(result['data'])):
            try:
                res = (result['data'][i]['vulns'].keys())
                res = json.loads(res.encode('utf-8'))
                respSet.update(res)
            except:
                pass

        return list(respSet)
    except:
        return []

def shodanQuery(query):
    return api.search(query)
