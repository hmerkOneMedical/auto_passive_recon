## TODO: test addition of whois

__author__ = 'helena merk'

from flask import Flask, render_template, request, Response, jsonify, url_for, redirect
from celery import Celery

import json
from scripts.recon import run_recon
import string
import os
import requests
from selenium import webdriver
import base64
import time
import random
import redis

from scripts import *
from scripts.helpers import *
from scripts.render_helpers import *

from scripts.domain_enumeration import *

app = Flask(__name__, static_url_path='/static')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')


app.config['CELERY_BROKER_URL'] = redis_url
app.config['CELERY_RESULT_BACKEND'] = redis_url

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

printable = set(string.printable)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/frame')
def frame():
    try:
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
    except:
        return '<div style="max-width: 100%; height: auto"><h3>Something went wrong with headless chrome driver.</h3></div>'

## Statically renders report template ==> works only on localhost.
@app.route('/recon', methods=['POST'])
def recon():
    company_url = request.form['company_url']
    company_name = (request.form['company_name']).lower()
    current_ip = os.environ.get('HOSTED_IP', '127.0.0.1:5000')

    local = False
    if current_ip == '127.0.0.1:5000':
        local = True

    response = run_recon(company_url, company_name, None, False, local)
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

    

    return render_template('report_details.html', EXPOSED_IP=current_ip, whois_result=whois_result, company_name=company_name, details=details, jobs=jobs, employees=employees, domain_results=domain_results, founder_emails=founder_emails)

## Renders dynamically. Why? Heroku limits requests to 30 seconds, and /recon route times out.
### Note. This still does not work! the sublist3r method takes too long.
@app.route('/report', methods=['POST'])
def report():
    current_ip = os.environ.get('HOSTED_IP', '127.0.0.1:5000')

    company_url = request.form['company_url']
    company_name = (request.form['company_name']).lower()

    ## cannot at the moment run sublist3r when hosted. :(
    if current_ip != '127.0.0.1:5000':
        return redirect(url_for('async_recon_report'), code=307))

    def generate():
        yield report_header_html(company_name)

        details = scrape_crunchbase.run_basics(company_name)
        whois_details = whois.whois(company_url)
        details['whois_details'] = whois_details
        
        yield details_html(details) 
        yield report_summary_html()
    
        founder_emails = []
        if details:
            for founder in details['founders']:
                founder_emails.append(hunter.get_work_email(company_url, founder))

        yield non_automated_checks(company_name, founder_emails)

        scrape_employees_query = google_scraper.query('site:www.linkedin.com/in \'' + company_name + '\' security cyber', 10)

        scrape_jobs_query = google_scraper.query(
        'site:www.linkedin.com/jobs \'' + company_name + '\' security cyber', 10)

        yield linkedin_details_html(scrape_employees_query, scrape_jobs_query)

        ## REPLACE this with async request !
        #subdomains = get_subdomains(company_url)
        subdomains = sublist3r.main(company_url, None, ports=None, silent=True, verbose=True, engines=None)
 
        yield '<br>'
        domain_results = query_shodan.add_domain_details(subdomains) #str(domain_results)
        yield domain_html(domain_results)
        ##

        yield report_footer_html()
    
    return Response(generate(), mimetype='text/html')


## What is Celery? Allows async functions running on a seperate worker. 
# 1. CELERY TASK  
#     @celery.task(bind=True)
#     def celery_task_func(self, arg1, arg2):
#        updates status, sends requests, etc.

# 2. START CELERY TASK WITH ARGUMENTS
#     // can happen anywhere. return endpoint for status checks
#     task = celery_task_func.apply_async(args=(arg1, arg2))
#     return jsonify({}), 202, {'Location': url_for('STATUS_ENDPOINT', task_id=task.id)}

# 3. STATUS_ENDPOINT/<task_id>
#     task = celery_task_func.AsyncResult(task_id)
#     from task.state, determine what response should be. Reformat, etc.
#     return jsonify(response)
 


## Launching celery: 
# upgrade worker
# launch redis db.


## Actual task that finds content
@celery.task(bind=True)
def async_recon(self, url, company_name):
    """Background task retrieving subdomain information"""
    total = 10
    growing_inner = {}
    #growing_html = ''
    print('celery task under works')
    print(url)
    
    self.update_state(state='PROGRESS', meta={'url': url, 'current': 1, 'total': total, 'status': 'Getting company basics', 'result': growing_inner})

    details = scrape_crunchbase.run_basics(company_name)
    #growing_html += details_html(details) 
    whois_details = whois.whois(url)
    details['whois_details'] = whois_details

    growing_inner['company-details'] = company_details(details)
    self.update_state(state='PROGRESS', meta={'current': 2, 'total': total, 'status': 'Getting summary', 'result': growing_inner})
    
    #growing_html += report_summary_html()
    self.update_state(state='PROGRESS', meta={'current': 3, 'total': total, 'status': 'Getting founders', 'result': growing_inner})

    founder_emails = []
    if details:
        for founder in details['founders']:
            founder_emails.append(hunter.get_work_email(url, founder))

   
    #growing_html += non_automated_checks(company_name, founder_emails)
    growing_inner['founder-emails-compro'] = founder_emails_compro(company_name, founder_emails)
    self.update_state(state='PROGRESS', meta={'current': 4, 'total': total, 'status': 'Getting subdomains', 'result': growing_inner})

    try:
        scrape_employees_query = google_scraper.query('site:www.linkedin.com/in \'' + company_name + '\' security cyber', 10)

        scrape_jobs_query = google_scraper.query(
            'site:www.linkedin.com/jobs \'' + company_name + '\' security cyber', 10)

        #growing_html += linkedin_details_html(scrape_employees_query, scrape_jobs_query)
        growing_inner['linkedin-details-inner'] = linkedin_details_inner(scrape_employees_query, scrape_jobs_query)
    except:
        growing_inner['linkedin-details-inner'] = 'Google has blocked this query :/'

    self.update_state(state='PROGRESS', meta={'current': 5, 'total': total, 'status': 'Getting subdomains', 'result': growing_inner})

    subdomains = get_subdomains(url)
    subdomains.append(url)

    self.update_state(state='PROGRESS', meta={'current': 6, 'total': total, 'status': 'Getting subdomain vulnerabilities', 'result': growing_inner})

    domain_results = query_shodan.add_domain_details(subdomains) #str(domain_results)

    #growing_html += domain_html(domain_results)
    growing_inner['domain-details-inner'] = domain_details_inner(domain_results)

    return {'state': 'COMPLETED', 'current': 100, 'total': 100, 'status': 'Task completed!', 'result': growing_inner}


# returns status of recon attempt 
@app.route('/report_status/<task_id>')
def report_status(task_id):
    task = async_recon.AsyncResult(task_id)
    if task.state == 'STARTED':
        response = {
            'state': task.state,
            'status': 'Starting...',
            'current': 1,
            'total': 3,
        }
    elif task.state == 'PROGRESS':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', ''),
            'result': task.info.get('result', {})
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'status': 'COMPLETED',
            'current': 2,
            'total': 2,
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else: # error
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)

@app.route('/launch_recon', methods=['POST'])
def launch_recon():
    url = str(request.json['url'])
    url = url.replace(" ", "")
    company_name = str(request.json['company_name'])
    task = async_recon.apply_async(args=[url, company_name])
    return jsonify({}), 202, {'Location': url_for('report_status', task_id=task.id)}

@app.route('/async_recon_report', methods=['GET', 'POST'])
def async_recon_report():
    if request.method == 'POST':
        company_url = request.form['company_url']
        company_name = (request.form['company_name']).lower()
        return render_template('async_report.html', DOMAIN=company_url, company_name=company_name)

    if request.method == 'GET':
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
