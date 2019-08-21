import shodan
import os
import json
import requests
import threading

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


def add_domain_details(subdomains):
    threads = list()
    domainDict = domainsToIPs(subdomains)
    ipResults = []
    for key, value in domainDict.iteritems():
        domainIps = domainDict[key]
        if len(domainIps) == 0:
            continue; # if site does not have an ip address, do not add it to reported subdomains!

        x = threading.Thread(target=threaded_domain, args=(domainIps,key, ipResults))
        threads.append(x)
        x.start() 

    for thread in (threads):
        thread.join()

    return ipResults

def threaded_domain(domainIps, key, ipResults):    
    vulns = []
    ports = []

    liveURL = False
    for ip in domainIps:
        try:
            
            res = api.host(ip)
            print(res)
            #[u'data', u'city', u'region_code', u'tags', u'ip', u'isp', u'area_code', u'dma_code', u'last_update', u'country_code3', u'latitude', u'hostnames', u'postal_code', u'longitude', u'country_code', u'org', u'country_name', u'ip_str', u'os', u'asn', u'ports']
            if 'ports' in res.keys():
                ports.extend(res['ports'])
                liveURL = True

            if 'vulns' in res.keys():
                print('VULNS FOUND')
                print(res['vulns'])
                vulns.extend(res['vulns'])
                liveURL = True
                
                print('HERE')
                print(vulns)

            if 'data' in res.keys():
                liveURL = True
                try:
                    for x in res['data']:
                        if 'vulns' in x['opts']:
                            print('updating!')
                            print x['opts']['vulns']
                            try:
                                vulns.extend(x['opts']['vulns'])
                            except:
                                pass
                        if 'http' in x.keys():
                            # print '[+] HTTP port present:\t'
                            # print '\tTitle: %s' % x['http']['title']
                            # print '\tRobots: %s' % x['http']['robots']
                            # print '\tServer: %s' % x['http']['server']
                            # print '\tComponents: %s' % x['http']['components']
                            # print '\tSitemap: %s' % x['http']['sitemap']

                            liveURL = True
                except:
                    pass

        except:
            pass

    print('vulns made it?')
    print(vulns)
    if liveURL:
        if vulns == None:
            vulns = []
        
        builtwith_results = get_technical_details(key)
        addition = {'url': key, 'ips': domainIps, 'vulns': vulns, 'ports': remove_dups(ports), 'builtwith': builtwith_results}
        ipResults.append(addition)
        print(addition)


def remove_dups(duped):
    return list(dict.fromkeys(duped))

def find_ip_vulnerabilities(ip):
    print(ip)
    print('???')
    return ip
    try:
        result = api.host(ip)
        respSet = set([])
        print(result['vulns'])
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
