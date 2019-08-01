__author__ = 'helena'

from flask import Flask, render_template, request
import json
from scripts.recon import run_recon
import string
import os
import requests
from selenium import webdriver
import base64
import uuid

app = Flask(__name__, static_url_path='/static')

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
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)

    screenshot = driver.get_screenshot_as_png()
    image_64_encoded = base64.encodestring(screenshot)
    decodedScreenie = "data:image/png;base64,%s" % image_64_encoded.decode("utf8")

    driver.close()

    return '<div style="max-width: 100%; height: auto"><img style="max-width: 100%; height: auto" src="'+decodedScreenie+'"/></div>'

@app.route('/recon', methods=['POST'])
def recon():
    company_url = request.form['company_url']
    company_name = (request.form['company_name']).lower()

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

    print domain_results

    current_ip = os.getenv('NGROK_EXPOSED_IP', '0.0.0.0')

    return render_template('report_details.html', EXPOSED_IP=current_ip, whois_result=whois_result, company_name=company_name, details=details, jobs=jobs, employees=employees, domain_results=domain_results, founder_emails=founder_emails)


# @app.route('/printing_test')
# def printing_test():
#     return render_template('printing_test.html')

# @app.route('/tests')
# def tests():
    
#     jobs = [{'description': '4 days ago - Provides advice and guidance on security strategies to manage identified ... Maintains current knowledge of malware attacks, and other cyber\xa0...', 'link': 'https://www.linkedin.com/jobs/view/senior-manager-information-security-at-adidas-1335984743?trk=guest_job_details_job_title', 'title': 'adidas hiring Senior Manager Information Security in Portland, OR, US ...'}, {'description': 'Jul 9, 2019 - The Cyber Security Risk Assessor identifies cyber security risks to HP assets utilizing defined\u2026See this and similar jobs on LinkedIn.', 'link': 'https://www.linkedin.com/jobs/view/cyber-security-risk-assessor-governance-risk-and-compliance-at-hp-1363229618', 'title': 'HP hiring Cyber Security Risk Assessor - Governance Risk and ...'}, {'description': 'adidasPortland, OR, US. 3 months ago Be among ... ', 'link': 'https://www.linkedin.com/jobs/view/director-information-security-csirt-at-adidas-1300484323', 'title': 'adidas hiring Director Information Security CSIRT in Portland, OR, US ...'}, {'description': 'Protect the enterprise against potential cyber-attacks. Play a key role in all CSIRT (Cyber Security Incident Response Team) activities, responding to potential\xa0...', 'link': 'https://www.linkedin.com/jobs/view/manager-cyber-security-incident-response-forensics-m-f-d-at-adidas-1108039796?trkInfo=searchKeywordString%3AComputer%2BForensics%2CsearchLocationString%3A%252C%2B%2Cvertical%3Ajobs%2CpageNum%3A0%2Cposition%3A7%2CMSRPsearchId%3Ab338c090-d2cf-48ec-bb06-1199acd1c1d6&refId=b338c090-d2cf-48ec-bb06-1199acd1c1d6&trk=jobs_jserp_job_listing_text', 'title': 'adidas hiring Manager Cyber Security Incident Response & Forensics ...'}, {'description': 'Senior IT Consultant, Application Security. adidasPortland, OR, US. 8 months ago Be in the first 30 applicants. No longer accepting applications\xa0...', 'link': 'https://www.linkedin.com/jobs/view/senior-it-consultant-application-security-at-adidas-932600104', 'title': 'adidas hiring Senior IT Consultant, Application Security in Portland ...'}, {'description': 'adidasHerzogenaurach, DE. 5 months ago Be in the first 30 .... Consultant (m/w/d) f\xfcr Cyber Security und Informationssicherheit. univativ GmbH. Stuttgart, DE.', 'link': 'https://www.linkedin.com/jobs/view/senior-manager-information-security-governance-m-f-d-at-adidas-1042474708?trkInfo=searchKeywordString%3AAdidas%2BGroup%2BSenior%2CsearchLocationString%3A%252C%2B%2Cvertical%3Ajobs%2CpageNum%3A1%2Cposition%3A10%2CMSRPsearchId%3A15c032c4-0c56-4a7a-acd3-b7ee66e4762c&refId=15c032c4-0c56-4a7a-acd3-b7ee66e4762c&trk=jobs_jserp_job_listing_text', 'title': 'adidas hiring Senior Manager Information Security Governance (m/f/d ...'}, {'description': 'Operations Engineer - Network Security. adidasPortland, OR, US. 3 months ago Be among the first 25 applicants. No longer accepting applications\xa0...', 'link': 'https://www.linkedin.com/jobs/view/operations-engineer-network-security-at-adidas-1278439970', 'title': 'adidas hiring Operations Engineer - Network Security in Portland, OR ...'}, {'description': 'adidasHerzogenaurach, DE ... Responsibility for Security Governance Management< Proactively identify security gaps and support .... Solutions Engineer (Cyber Security Services) - Amsterdam, Netherlands - (Remote) - Secureworks Sales.', 'link': 'https://www.linkedin.com/jobs/view/1242624856?trk=d_flagship3_salary_explorer&refId=ff31e0e9-c8ce-4e56-8f81-e744cab2dd9c', 'title': 'adidas hiring Senior Manager Information Security ... - LinkedIn'}, {'description': "The Senior Information Security Architect is responsible for ensuring the completeness (fitness-for-purpose) and integrity of adidas' information security architecture, ... business requirements with information and cyber security requirements.", 'link': 'https://www.linkedin.com/jobs/view/senior-information-security-architect-at-adidas-group-1294186653?trk=jobs_job_title', 'title': '\u963f\u8fea\u8fbe\u65af hiring Senior Information Security Architect in Shanghai ...'}, {'description': 'Jul 8, 2019 - Group Manager, Information Security-&amp;amp;gt;&amp;amp;gt; Manages a ... and tacklingcomplex cyber security problems from strategy to execution. .... Senior Manager Information Security. adidas. Portland, OR, US.', 'link': 'https://www.linkedin.com/jobs/view/group-manager-information-security-threat-detection-at-efinancialcareers-1346274849', 'title': 'eFinancialCareers hiring Group Manager Information Security - Threat ...'}] 
#     for job in jobs:
#         job['description'] = filter(lambda x: x in printable, job['description'])

#     domain_results = [{'url': 'https://www.wikipedia.com', 'ip':'0.0.0.0', 'vulns':'123-Abs'}]
#     return render_template('tests.html', data=jobs, domain_results=domain_results)


# @app.route('/linkPreviews', methods=['GET'])
# def linkPreviews():
#     key = os.environ['LINKPREVIEW_API_KEY'];
#     return (requests.get('http://api.linkpreview.net/?key='+key+'&q=https://www.onemedical.com')).json()




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3003)
