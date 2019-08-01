import shodan
import os
import json
import requests

from helpers import *

SHODAN_API_KEY = os.environ['SHODAN_API_KEY']
api = shodan.Shodan(SHODAN_API_KEY)

def dns_resolve(hostnames):
    url = 'https://api.shodan.io/dns/resolve?hostnames={}&key={}'.format(hostnames, SHODAN_API_KEY)

    # Sample Response:
    #  {
    #  "google.com": "74.125.227.230",
    #  "bing.com": "204.79.197.200"
    # }
    return (requests.get(url)).json()


def get_domain_vulnerabilites(subdomains):
    domainDict = domainsToIPs(subdomains)
    ipResults = []
    for key, value in domainDict.iteritems():
        vulns = []
        domainIps = domainDict[key]
        ports = []

        if len(domainIps) == 0:
            continue; # if site does not have an ip address, do not add it to reported subdomains!

        liveURL = False
        for ip in domainIps:
            try:
                res = api.host(ip)
                #[u'data', u'city', u'region_code', u'tags', u'ip', u'isp', u'area_code', u'dma_code', u'last_update', u'country_code3', u'latitude', u'hostnames', u'postal_code', u'longitude', u'country_code', u'org', u'country_name', u'ip_str', u'os', u'asn', u'ports']
                if 'ports' in res.keys():
                    ports.extend(res['ports'])
                    liveURL = True

                if 'vulns' in res.keys():
                    vulns.extend(res['vulns'])
                    liveURL = True

                if 'data' in res.keys():
                    liveURL = True
                    try:
                        for x in res['data']:
                            print x.keys()
                            if 'vulns' in x['opts']:
                                print('updating!')
                                print x['opts']['vulns']
                                try:
                                    vulns = vulns.extend(x['opts']['vulns'])
                                except:
                                    print 'here'
                                    pass
                            if 'http' in x.keys():
                                print '[+] HTTP port present:\t'
                                print '\tTitle: %s' % x['http']['title']
                                print '\tRobots: %s' % x['http']['robots']
                                print '\tServer: %s' % x['http']['server']
                                print '\tComponents: %s' % x['http']['components']
                                print '\tSitemap: %s' % x['http']['sitemap']

                                liveURL = True
                    except:
                        pass

            except:
                pass

        if liveURL:
            if vulns == None:
                vulns = []

            addition = {'url': key, 'ips': domainDict[key], 'vulns': vulns, 'ports': ports}
            ipResults.append(addition)
            print(addition)

    return ipResults


def find_ip_vulnerabilities(ip):
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

def shodan_query(query):
    return api.search(query)
