import shodan
import os
from helpers import *

SHODAN_API_KEY = os.environ['SHODAN_API_KEY']
api = shodan.Shodan(SHODAN_API_KEY)

def getDomainVulnerabilites(subdomains):
    ips = domainsToIPs(subdomains)
    ipResults = {}
    for ip in ips:
        ipResults[ip] = findVulnerabilitiesWithIp(ip)

    return ipResults


def findVulnerabilitiesWithIp(ip):
    result = api.host(ip)
    respSet = set([])
    for i in range(0, len(result['data'])):
        try:
            res = (result['data'][i]['vulns'].keys())
            res = json.loads(res.encode('utf-8'))
            respSet.update(res)
        except:
            pass

    return respSet

def shodanQuery(query):
    return api.search(query)
