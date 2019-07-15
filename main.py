## CALL ALL HELPERS
import os

import scrapeCrunchbase
import sublist3r 
import whois
import googleScraper
import json
import shodan

SHODAN_API_KEY = os.environ['SHODAN_API_KEY']


Gr = '\033[90m'   # grey
G = '\033[92m'  # green
Y = '\033[93m'  # yellow
B = '\033[94m'  # blue
R = '\033[91m'  # red
W = '\033[0m'   # white
BOLD = '\033[1m'
END = '\033[0m'

def formatInput(promter):
    return raw_input(BOLD + promter+ END + ' \n>>  ')

def pprint(log, indent, unwanted_keys):
    tabs = indent*'\t' or ''
    if (isinstance(log, str) or (isinstance(log, int))):
        print(tabs+str(log))
    elif (isinstance(log,list)):
        try:
            print(tabs + ', '.join(log))
        except:
                for item in log:
                    if (isinstance(item, str) or (isinstance(item, int))):
                        print(tabs + str(item))
                    else:
                        pprint(item, indent+1, unwanted_keys)
                    print('\n')
    elif (isinstance(log, dict)):
        if unwanted_keys:
            for unwanted_key in unwanted_keys: 
                if unwanted_key in log:
                    del log[unwanted_key]

        for key in log.keys():
            if isinstance(log[key], str) or isinstance(log[key], int):
                print(tabs+key+': '+str(log[key]))
            else:
                print(tabs+''+key+':')
                pprint(log[key], indent+1, unwanted_keys)
    elif (isinstance(log, unicode)):
        pprint(log.encode('utf-8'), indent, unwanted_keys)
    else:
        print(str(tabs)+str(log))

def formatResponse(title, log = '', unwanted_keys = []):
    print("%s==========================%s" % (Gr, W))
    print("%s%s%s%s%s" % (B, BOLD, title, W, END))
    print(pprint(log, 0, unwanted_keys))
    
#==================

companyUrl = formatInput('URL')
companyName = formatInput('NAME')
subdomainOutFile = formatInput('FILE PATH FOR SUBDOMAINS (use .txt extension)')

try:
    basics = (scrapeCrunchbase.companyBasicInfo(companyName))
    formatResponse('Basic Company Information (Crunchbase)', basics, [])
except:
    formatResponse('no crunchbase record for company named '+ companyName, '', [])


domain = whois.query(companyUrl)
scrape_employees_query = googleScraper.query('site:www.linkedin.com/in security cyber ' + companyName, 10)
scrape_jobs_query = googleScraper.query('site:www.linkedin.com/jobs security cyber ' + companyName, 10)
unwanted_keys = ['rank', 'keyword']

runSublist3r = formatInput('Would you like to run sublist3r? (yes/no)')

if (runSublist3r == 'yes'):
    formatResponse('Enumerated Subdomains (sublist3r)', '...',[])
    try:
        subdomains = sublist3r.main(companyUrl, subdomainOutFile, ports= None, silent=False, verbose=True, engines=None)
        formatResponse('SUBDOMAIN COUNT:', str(len(subdomains)), [])
    except e:
        print(e)


formatResponse('WhoIs Results', json.loads(domain.encode('utf-8')), [])
formatResponse('Linkedin Hits for Currently Employed In Security/Cyber', scrape_employees_query, unwanted_keys)
formatResponse('Linkedin Hits for Security/Cyber Jobs Listed', scrape_jobs_query, unwanted_keys)


runShodan = formatInput('Would you like to run Shodan? (yes/no)')

if runShodan == 'yes':
    searchQuery = formatInput('Modify Search Query? (Default: '+companyName+')')
    if not searchQuery:
        searchQuery = companyName

    runVerbose = formatInput('Verbose? (yes/no)')
    shodanapi = shodan.Shodan(SHODAN_API_KEY)
    try:
            # Search Shodan
            results = shodanapi.search(searchQuery)

            # Show the results
            print('Results found: {}'.format(results['total']))
            if runVerbose == 'yes':
                formatResponse('Shodan Results Found: ', results['matches'], ['html', 'data', 'references'])
            else:
                try:
                    print(results['matches'][0].keys())
                except:
                    print('No matches.')
    except shodan.APIError, e:
            print('Error: {}'.format(e))

else:
    print('Not running shodan... ')