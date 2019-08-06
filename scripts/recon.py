# CALL ALL HELPERS
import os

import scrape_crunchbase
import sublist3r
import whois
import google_scraper
import json
from query_shodan import *
from hunter import *
from helpers import *
from constants import *
from domain_enumeration import *

# ==================

def run_recon(company_url, company_name, subdomain_out_file, interactive, run_sublist3r='yes', runShodan='no', local=True):
    subdomains = []
    domain_results = {}
    data = {}
    run_verbose = 'no'
    run_sublist3r='yes'
    unwanted_keys = ['rank', 'keyword']

    details = scrape_crunchbase.run_basics(company_name)

    founder_emails = []
    if details:
        for founder in details['founders']:
            founder_emails.append(get_work_email(company_url, founder))

    format_print_response('Founder Emails', founder_emails)

    if interactive: formatInput('Press `return` to continue.')

    print(company_url)
    company_url = str(company_url)
    try:
        whois_result = whois.query(company_url)
        whois_result = json.loads(whois_result.encode('utf-8'))
    except:
        whois_result = {'data': []}

    scrape_employees_query = google_scraper.query(
        'site:www.linkedin.com/in \'' + company_name + '\' security cyber', 10)
    scrape_jobs_query = google_scraper.query(
        'site:www.linkedin.com/jobs \'' + company_name + '\' security cyber', 10)

    format_print_response('WhoIs Results', whois_result, [])
    
    if interactive: formatInput('Press `return` to continue.')

    format_print_response('Linkedin Hits for Currently Employed In Security/Cyber', scrape_employees_query, unwanted_keys)
    if interactive: formatInput('Press `return` to continue.')
    
    format_print_response('Linkedin Hits for Security/Cyber Jobs Listed', scrape_jobs_query, unwanted_keys)

    if interactive: run_sublist3r = formatInput('Would you like to run sublist3r? (yes/no)')

    if (run_sublist3r == 'yes'):
        format_print_response('Searching for Subdomains (sublist3r)', '...will be saved to specified file.', [])
        try:
            if local:
                subdomains = sublist3r.main(company_url, subdomain_out_file, ports=None, silent=True, verbose=True, engines=None)
            else:
                subdomains = get_subdomains(company_url)
            format_print_response('Subdomain Count:', str(len(subdomains)), [])

            if len(subdomains) > 0:
                print('evaluating.')
                domain_results = add_domain_details(subdomains)
                format_print_response('Shodan Identified the following CVEs (Visit https://nvd.nist.gov/vuln/detail/CVE-[xxxx]-[xxxx])', domain_results)

        except Exception as e:
            print(e)

    if interactive:
        runShodan = formatInput('Would you like to run Shodan? (yes/no)')
    while runShodan == 'yes':
        if interactive:
            search_query = formatInput(
                'Enter Search Query (Default: '+company_name+')')
        if not search_query:
            search_query = company_name

        if interactive:
            run_verbose = formatInput('Verbose? (yes/no)')

        try:
            results = shodan_query(search_query)
            print('Results found: {}'.format(results['total']))
            if run_verbose == 'yes':
                format_print_response('Shodan Results Found: ', results['matches'], ['html', 'data', 'references'])
        except shodan.APIError, e:
            print('Error: {}'.format(e))

        if not interactive: runShodan = False
        else:
            runShodan = formatInput('Would you like to run Shodan again? (yes/no)')
    else:
        print('Done with shodan')

    
    data = {
        'domain_results': domain_results, 
        'employees': scrape_employees_query,
        'jobs': scrape_jobs_query,
        'details': details,
        'founder_emails': founder_emails,
        'whois_result': whois_result['data'],
    }

    if not interactive:
        return data

    print(BOLD+'################## Report #####################'+END)
    if subdomains and len(subdomains) > 20:
        print('Large number of subdomains may pose greater security risk.')

    security_mentions = 0
    for human in scrape_employees_query:
        security_mentions += human['description'].count(
            'Security') + human['description'].count('cyber')
    if security_mentions < 20:
        print(errors['security_eng'])

    security_hiring = 0
    for human in scrape_jobs_query:
        security_hiring += human['description'].count('Security') + human['description'].count('cyber')
    
    if security_hiring < 10:
        print('Not hiring significant security staff')
        print(errors['security_eng_hiring'])

    print(errors['standard_disclosure'])


if __name__ == '__main__':
    company_url = formatInput('URL')
    company_name = formatInput('NAME (as listed on crunchbase)')
    subdomain_out_file = formatInput(
        'Please supply a filepath for output of subdomain enumeration (use .txt extension)')
    interactive = True
    run_recon(company_url, company_name, subdomain_out_file, interactive, True)