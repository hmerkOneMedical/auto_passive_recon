__author__ = 'helena merk'

from flask import Flask, render_template, request, Response, session

import json
from scripts.recon import run_recon
import string
import os
import requests
from selenium import webdriver
import base64
import time

from scripts import *
from scripts.helpers import *
from scripts.render_helpers import *

app = Flask(__name__, static_url_path='/static')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

printable = set(string.printable)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/frame')
def frame():
    url = request.args.get('url')
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--test-type")
    options.add_argument("--headless")
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)

    screenshot = driver.get_screenshot_as_png()
    image_64_encoded = base64.encodestring(screenshot)
    decodedScreenie = "data:image/png;base64,%s" % image_64_encoded.decode("utf8")

    driver.close()

    return '<div style="max-width: 100%; height: auto"><img style="max-width: 100%; height: auto" src="'+decodedScreenie+'"/></div>'

## Statically renders report template
@app.route('/recon', methods=['POST'])
def recon():
    company_url = request.form['company_url']
    company_name = (request.form['company_name']).lower()

    session['company_url'] = company_url
    session['company_name'] = company_name

    response = run_recon(company_url, company_name, None, False)
    details = response['details']
    domain_results = response['domain_results']
    employees = response['employees']
    jobs = response['jobs']
    founder_emails = response['founder_emails']
    whois_result = response['whois_result']

    for job in jobs:
        job['description'] = filter(lambda x: x in printable, job['description'])

    for job in employees:
        job['description'] = filter(lambda x: x in printable, job['description'])

    current_ip = os.getenv('NGROK_EXPOSED_IP', '0.0.0.0')

    return render_template('report_details.html', EXPOSED_IP=current_ip, whois_result=whois_result, company_name=company_name, details=details, jobs=jobs, employees=employees, domain_results=domain_results, founder_emails=founder_emails)

## Renders dynamically. Why? Heroku limits requests to 30 seconds, and /recon route times out.
@app.route('/report', methods=['POST'])
def report():
    current_ip = os.getenv('NGROK_EXPOSED_IP', '127.0.0.1:5000')

    company_url = request.form['company_url']
    company_name = (request.form['company_name']).lower()

    session['company_url'] = company_url
    session['company_name'] = company_name

    def format_json_save(key, value):
        session[key] = json.dumps(value)

    def callback_for_saving(data):
        for key, val in data.iteritems():
            format_json_save(key, value)

    def generate():
        #session['test'] = 'yes'
        yield report_header_html(company_name)

        details = scrape_crunchbase.run_basics(company_name)
        
        yield details_html(details) 

        yield report_summary_html()
    
        founder_emails = []
        if details:
            for founder in details['founders']:
                founder_emails.append(hunter.get_work_email(company_url, founder))

        yield non_automated_checks(company_name, founder_emails)

        # yield 'Step 3: Scraping the web...<br>' #str(founder_emails)

        scrape_employees_query = google_scraper.query('site:www.linkedin.com/in \'' + company_name + '\' security cyber', 10)

        scrape_jobs_query = google_scraper.query(
        'site:www.linkedin.com/jobs \'' + company_name + '\' security cyber', 10)

        yield linkedin_details_html(scrape_employees_query, scrape_jobs_query)

        subdomains = sublist3r.main(
                company_url, None, ports=None, silent=True, verbose=True, engines=None)

        
        
        domain_results = query_shodan.add_domain_details(subdomains) #str(domain_results)
        yield domain_html(domain_results)
        # # format_json_save('domain_results', domain_results)

        # data = {
        #     'domain_results': domain_results, 
        #     'employees': scrape_employees_query,
        #     'jobs': scrape_jobs_query,
        #     'details': details,
        #     'founder_emails': founder_emails,
        #     'whois_result': whois_result['data'],
        # }

        yield report_footer_html()
    
    return Response(generate(), mimetype='text/html')

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=3003)
    app.run()
