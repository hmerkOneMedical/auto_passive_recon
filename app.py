## TODO: test addition of whois

__author__ = 'helena merk'

from flask import Flask, render_template, request, Response, jsonify, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_heroku import Heroku
from flask_marshmallow import Marshmallow
from werkzeug.security import generate_password_hash, check_password_hash
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
from scripts.render_helpers import *

from scripts.sublist1r import getSubdomains

app = Flask(__name__, static_url_path='/static')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


# Initialize Postgres and SQLAlchemy
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Create our database model
class Report(db.Model):
    __tablename__ = "reports"
    report_id = Column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False)
    is_complete = Column(Boolean, unique=False, default=False)
    result = db.Column(db.PickleType)    

    def __repr__(self):
        return '<Report id %r>' % self.report_id

    def __init__(self, report_id):
        self.report_id = report_id
        self.is_complete = False

class ReportSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('result')

report_schema = ReportSchema()

# Initialize Redis + Celery
redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

app.config['CELERY_BROKER_URL'] = redis_url
app.config['CELERY_RESULT_BACKEND'] = redis_url

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
    print(current_ip)
    if current_ip == '127.0.0.1:5000':
        local = True
    else:
        return redirect(url_for('async_recon_report'), code=307)

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

    if current_ip == '127.0.0.1:5000': #we can run sublist3r!
        local = True
    else:
        return redirect(url_for('async_recon_report'), code=307)

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
        subdomains = getSubdomains(company_url, None, ports=None, silent=True, verbose=True, engines=None)
        print(subdomains)

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
#     return jsonify({}), 202, {'Location': url_for('STATUS_ENDPOINT', report_id=task.id)}

# 3. STATUS_ENDPOINT/<report_id>
#     task = celery_task_func.AsyncResult(report_id)
#     from task.state, determine what response should be. Reformat, etc.
#     return jsonify(response)
 


## Launching celery: 
# upgrade worker
# launch redis db.

def get_subdomains_by_request(req):
    url = base_url + '/'
    requests.get()

## Actual task that finds content
@celery.task(bind=True)
def async_recon(self, company_url, company_name):
    """Background task retrieving subdomain information"""
    total = 10
    growing_inner = {}
    #growing_html = ''
    print('celery task under works')
    print(company_url)

    growing_inner['company_url'] = company_url
    growing_inner['company_name'] = company_name
    
    self.update_state(state='PROGRESS', meta={'company_url': company_url, 'current': 1, 'total': total, 'status': 'Getting company basics', 'result': growing_inner})

    details = scrape_crunchbase.run_basics(company_name)
    #growing_html += details_html(details) 
    whois_details = whois.whois(company_url)
    details['whois_details'] = whois_details

    growing_inner['company-details'] = company_details(details)
    self.update_state(state='PROGRESS', meta={'current': 2, 'total': total, 'status': 'Getting summary', 'result': growing_inner})
    
    #growing_html += report_summary_html()
    self.update_state(state='PROGRESS', meta={'current': 3, 'total': total, 'status': 'Getting founders', 'result': growing_inner})

    founder_emails = []
    if details:
        for founder in details['founders']:
            founder_emails.append(hunter.get_work_email(company_url, founder))

   
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

    #subdomains = get_subdomains(company_url)
    #subdomains.append(company_url)

    subdomains = getSubdomains(company_url, None, ports=None, silent=True, verbose=True, engines=None)

    self.update_state(state='PROGRESS', meta={'current': 6, 'total': total, 'status': 'Getting subdomain vulnerabilities', 'result': growing_inner})

    domain_results = query_shodan.add_domain_details(subdomains) #str(domain_results)

    #growing_html += domain_html(domain_results)
    growing_inner['domain-details-inner'] = domain_details_inner(domain_results)

    return {'state': 'COMPLETED', 'current': 100, 'total': 100, 'status': 'Task completed!', 'result': growing_inner}


# returns status of recon attempt 
@app.route('/report_status/<report_id>')
def report_status(report_id):
    # check if is_complete returns true from postgres. else, check async result.
    report = Report.query.get(report_id)
    print('REPORT FINDING HERE')
    print(report)
    if (report and report.is_complete):
        res = report_schema.jsonify(report)
        response = {
            'state': 'COMPLETED',
            'status': 'COMPLETED',
            'current': 1,
            'total': 1,
            'result': res
        }
        print('returning from postgres hehe')
        return jsonify(response)

    ## get async report 
    task = async_recon.AsyncResult(report_id)
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
            ## update db info
            report.result = response['result']
            report.is_complete = True
            db.session.commit()
            ##

            response['result'] = task.info['result']
    else: # error
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)

# @app.route('/launch_recon', methods=['POST'])
# def launch_recon():
#     url = str(request.json['url'])
#     url = url.replace(" ", "")
#     company_name = str(request.json['company_name'])
#     task = async_recon.apply_async(args=[url, company_name])
#     return jsonify({}), 202, {'Location': url_for('report_status', report_id=task.id)}
def send_report(company_name, message_url):
    MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY', '')
    MAILGUN_DOMAIN = os.environ.get('MAILGUN_DOMAIN', '')
    MAILGUN_SMTP_LOGIN = os.environ.get('MAILGUN_SMTP_LOGIN', '')
    HOSTED_IP = os.environ.get('HOSTED_IP', '')
    return requests.post(
		"https://api.mailgun.net/v3/" + MAILGUN_DOMAIN + "/messages",
		auth=("api", MAILGUN_API_KEY),
		data={"from": "Automated Recon <" + MAILGUN_SMTP_LOGIN + ">",
			"to": "App Sec <hmerk@onemedical.com>",
			"subject": "Passive Recon Report: "+company_name,
			"text": "New passsive recon started! Check progress and get report here: " + HOSTED_IP + message_url})

@app.route('/async_recon_report', methods=['POST'])
def async_recon_report():
    if request.method == 'POST':
        company_url = request.form['company_url']
        company_name = (request.form['company_name']).lower()
        task = async_recon.apply_async(args=[company_url, company_name])
        task_indexed_url = url_for('report_details', report_id=task.id, _method='GET')
        
        # initializes value in postgres
        report = Report(report_id=task.id)
        db.session.add(report)
        db.session.commit()
        
        res = send_report(company_name, task_indexed_url)
        print(res.text)
        return redirect(task_indexed_url)

    if request.method == 'GET':
        return redirect(url_for('index'))

@app.route('/report_details/<report_id>', methods=['GET'])
def report_details(report_id):
    if request.method == 'GET':
        status_url = url_for('report_status', report_id=report_id)
        return render_template('async_report.html', STATUS_URL=status_url)

if __name__ == '__main__':
    app.run()
