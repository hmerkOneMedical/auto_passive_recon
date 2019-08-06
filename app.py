__author__ = 'helena merk'

from flask import Flask, render_template, request, Response, jsonify, url_for
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

print(redis_url)

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

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
    current_ip = os.environ.get('NGROK_EXPOSED_IP', '127.0.0.1:5000')

    # session['company_url'] = company_url
    # session['company_name'] = company_name
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
@app.route('/report', methods=['POST'])
def report():
    current_ip = os.environ.get('NGROK_EXPOSED_IP', '127.0.0.1:5000')

    company_url = request.form['company_url']
    company_name = (request.form['company_name']).lower()

    # session['company_url'] = company_url
    # session['company_name'] = company_name

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

        # scrape_employees_query = google_scraper.query('site:www.linkedin.com/in \'' + company_name + '\' security cyber', 10)

        # scrape_jobs_query = google_scraper.query(
        # 'site:www.linkedin.com/jobs \'' + company_name + '\' security cyber', 10)

        # yield linkedin_details_html(scrape_employees_query, scrape_jobs_query)

        ## REPLACE this with async request !
        subdomains = get_subdomains(company_url)
        #sublist3r.main(company_url, None, ports=None, silent=True, verbose=True, engines=None)
 
        yield '<br>'
        domain_results = query_shodan.add_domain_details(subdomains) #str(domain_results)
        yield domain_html(domain_results)
        ##


        yield report_footer_html()
    
    return Response(generate(), mimetype='text/html')

## Actual task that finds content
@celery.task(bind=True)
def async_sublister(self, url):
    print('celery task under works')
    print(url)
    """Background task retrieving subdomain information"""

    self.update_state(state='STARTED', meta={url: url})
    print('STARTED PROCESS WITH URL: ' + url)
    ## MULTITHREADING NOT ALLOWED
    #subdomains = sublist3r.main(url, None, ports=None, silent=True, verbose=True, engines=None)
    subdomains = get_subdomains(url)
    print('ack. subdomains')

    self.update_state(state='PROGRESS', meta={'subdomains':subdomains})

    domain_results = query_shodan.add_domain_details(subdomains) #str(domain_results)

    print('HI')
    
    self.update_state(state='COMPLETED', meta={'status': 'Task completed!', 'result': domain_results})
    return {'state': 'COMPLETED', 'status': 'Task completed!', 'result': domain_results}


# returns status of domain details 
@app.route('/report_status/<task_id>')
def report_status(task_id):
    task = async_sublister.AsyncResult(task_id)
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
            'status': 'PROGRESS...',
            'current': 1,
            'total': 2,
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'status': task.info.get('status', ''),
            'current': 1,
            'total': 1,
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
            response['html'] = domain_html(task.info['result'])
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)

@app.route('/start_sublister', methods=['POST'])
def start_sublister():
    print('hit')
    url = str(request.json['url'])
    print('starting sublister!!')
    print(url)
    url = url.replace(" ", "")
    params = {'url': url}
    task = async_sublister.apply_async(args=[url])
    return jsonify({}), 202, {'Location': url_for('report_status', task_id=task.id)}



## WTF is Celery? Allows async functions running on a seperate worker. 
# 1. kickoff function
#     task = func.apply_async(args, kwargs...)
#         return jsonify({}), 202, {'Location': url_for('STATUS_ENDPOINT', task_id=task.id)}
# 2. STATUS_ENDPOINT/<id>
#     task = func.AsyncResult(id)
#     from task.state, determine what response should be. Reformat, etc.
#     return jsonify(response)
# 3. func:
#     updates status, sends requests, etc. 

## Launching celery: 
# upgrade worker
# launch redis db.



## TODO: send get request to /start_sublister with url as an argument!!!

@app.route('/long_sublister_demo', methods=['GET', 'POST'])
def long_sublister_demo():
    if request.method == 'GET':
        return render_template('async_report.html', DOMAIN='onemedical.com')



#### Visit /long_task_demo to test async requests with celery :)
@celery.task(bind=True)
def long_task(self):
    print('hereeeeee')
    """Background task that runs a long function with progress reports."""
    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
    adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
    message = ''
    total = random.randint(10, 50)
    print('now here')
    for i in range(total):
        if not message or random.random() < 0.25:
            message = '{0} {1} {2}...'.format(random.choice(verb),
                                              random.choice(adjective),
                                              random.choice(noun))
        self.update_state(state='PROGRESS',
                          meta={'current': i, 'total': total,
                                'status': message})
        time.sleep(1)
    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 42}


@app.route('/long_task_demo', methods=['GET', 'POST'])
def long_task_demo():
    if request.method == 'GET':
        return render_template('long_task.html', )

    # # send the email
    # email_data = {
    #     'subject': 'Hello from Flask',
    #     'to': email,
    #     'body': 'This is a test email sent from a background Celery task.'
    # }
    # if request.form['submit'] == 'Send':
    #     # send right away
    #     send_async_email.delay(email_data)
    #     flash('Sending email to {0}'.format(email))
    # else:
    #     # send in one minute
    #     send_async_email.apply_async(args=[email_data], countdown=60)
    #     flash('An email will be sent to {0} in one minute'.format(email))

    return redirect(url_for('long_task_demo'))


@app.route('/longtask', methods=['POST'])
def longtask():
    print('hit')
    task = long_task.apply_async()
    print('help.')
    return jsonify({}), 202, {'Location': url_for('taskstatus',
                                                  task_id=task.id)}


@app.route('/status/<task_id>')
def taskstatus(task_id):
    task = long_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
            response['html'] = domain_html(task.info['result'])
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)


if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=3003)
    app.run()
