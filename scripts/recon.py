## CALL ALL HELPERS
import os

import scrapeCrunchbase
import sublist3r 
import whois
import googleScraper
import json
from queryShodan import *

from helpers import *
from constants import *

#==================
def runRecon(companyUrl, companyName, subdomainOutFile, interactive):
    subdomains = []
    ipResults = {}
    runSublist3r = 'yes'
    runVerbose = 'no'
    runShodan = 'no'

    scrapeCrunchbase.runBasics(companyName)
    if interactive: formatInput('Press `return` to continue.')

    domain = whois.query(companyUrl)
    scrape_employees_query = googleScraper.query('site:www.linkedin.com/in \"' + companyName + '\" security cyber ', 10)
    scrape_jobs_query = googleScraper.query('site:www.linkedin.com/jobs \"' + companyName + '\" security cyber ', 10)
    unwanted_keys = ['rank', 'keyword']

    formatResponse('WhoIs Results', json.loads(domain.encode('utf-8')), [])
    if interactive: formatInput('Press `return` to continue.')
    formatResponse('Linkedin Hits for Currently Employed In Security/Cyber', scrape_employees_query, unwanted_keys)
    if interactive: formatInput('Press `return` to continue.')
    formatResponse('Linkedin Hits for Security/Cyber Jobs Listed', scrape_jobs_query, unwanted_keys)

    if interactive: 
        runSublist3r = formatInput('Would you like to run sublist3r? (yes/no)')

    if (runSublist3r == 'yes'):
        formatResponse('Searching for Subdomains (sublist3r)', '...will be saved to specified file.',[])
        try:
            subdomains = sublist3r.main(companyUrl, subdomainOutFile, ports= None, silent=True, verbose=True, engines=None)
            formatResponse('Subdomain Count:', str(len(subdomains)), [])

            if len(subdomains) > 0:
                print('evaluating.')
                ipResults = getDomainVulnerabilites(subdomains)
                formatResponse('Shodan Identified the following CVEs (Visit https://nvd.nist.gov/vuln/detail/CVE-[xxxx]-[xxxx])', ipResults)

        except Exception as e:
            print(e)


    if interactive: runShodan = formatInput('Would you like to run Shodan? (yes/no)')
    while runShodan == 'yes':
        if interactive: searchQuery = formatInput('Enter Search Query (Default: '+companyName+')')
        if not searchQuery:
            searchQuery = companyName

        if interactive: runVerbose = formatInput('Verbose? (yes/no)')
        
        try:
            results = shodanQuery(searchQuery)
            print('Results found: {}'.format(results['total']))
            if runVerbose == 'yes':
                formatResponse('Shodan Results Found: ', results['matches'], ['html', 'data', 'references'])
        except shodan.APIError, e:
            print('Error: {}'.format(e))

        if not interactive:
            runShodan = False
        else:
            runShodan = formatInput('Would you like to run Shodan again? (yes/no)')
    else:
        print('Done with shodan')


    print(BOLD+"################## Report #####################"+END)
    if subdomains and len(subdomains) > 20:
        print('Large number of subdomains may pose greater security risk.')

    security_mentions = 0
    for human in scrape_employees_query:
        security_mentions += human['description'].count('Security') + human['description'].count('cyber')
    if security_mentions < 20:
        print(errors['security_eng'])

    security_hiring = 0
    for human in scrape_jobs_query:
        security_hiring += human['description'].count('Security') + human['description'].count('cyber')
    if security_hiring < 10:
        print('Not hiring significant security staff')
        print(errors['security_eng_hiring'])

    if ipResults.keys():
        print(ipResults.values())
        print('There are security vulnerabilites.')

    print(errors['standard_disclosure'])

    return {
        "subdomains": {"count":len(subdomains), "data": subdomains}, 
        'vulns': ipResults, "shodanResults": 
        'results', "employees": scrape_employees_query, 
        "jobs": scrape_jobs_query
    }

if __name__ == "__main__":
    companyUrl = formatInput('URL')
    companyName = formatInput('NAME')
    subdomainOutFile = formatInput('FILE PATH FOR SUBDOMAINS (use .txt extension)')
    interactive = True
    runRecon(companyUrl, companyName, subdomainOutFile, interactive)