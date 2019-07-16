## CALL ALL HELPERS
import os

import scrapeCrunchbase
import sublist3r 
import whois
import googleScraper
import json
from queryShodan import *

from helpers import *


#==================
companyUrl = formatInput('URL')
companyName = formatInput('NAME')
subdomainOutFile = formatInput('FILE PATH FOR SUBDOMAINS (use .txt extension)')

basics = (scrapeCrunchbase.companyBasicInfo(companyName))
formatResponse('Basic Company Information (Crunchbase)', basics, [])

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

        if len(subdomains) > 0:
            ipResults = getDomainVulnerabilites(subdomains)
            formatResponse('Shodan Identified the following CVEs', ipResults)

    except Exception as e:
        print(e)


formatResponse('WhoIs Results', json.loads(domain.encode('utf-8')), [])
formatResponse('Linkedin Hits for Currently Employed In Security/Cyber', scrape_employees_query, unwanted_keys)
formatResponse('Linkedin Hits for Security/Cyber Jobs Listed', scrape_jobs_query, unwanted_keys)

runShodan = formatInput('Would you like to run Shodan? (yes/no)')
while runShodan == 'yes':
    searchQuery = formatInput('Modify Search Query? (Default: '+companyName+')')
    if not searchQuery:
        searchQuery = companyName

    runVerbose = formatInput('Verbose? (yes/no)')
    
    try:
        results = shodanQuery(searchQuery)

        print('Results found: {}'.format(results['total']))
        if runVerbose == 'yes':
            formatResponse('Shodan Results Found: ', results['matches'], ['html', 'data', 'references'])
    except shodan.APIError, e:
        print('Error: {}'.format(e))

    runShodan = formatInput('Would you like to run Shodan again? (yes/no)')
else:
    print('Done with shodan')


