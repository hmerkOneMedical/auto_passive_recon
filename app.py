__author__ = 'helena'

from flask import Flask, render_template, request
import json
from scripts.recon import runRecon

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recon', methods=['POST'])
def recon():
    companyURL = request.form['companyURL']
    companyName = request.form['companyName']
    response = runRecon(companyURL, companyName, None, False)
    
    # example response 
    #response['vulns'] = {"52.214.233.75": ["CVE-2010-1256", "CVE-2010-2730", "CVE-2010-3972", "CVE-2010-1899", "CVE-2012-2531"], "52.31.227.42": ["CVE-2014-0117", "CVE-2014-0118", "CVE-2016-0736", "CVE-2015-3185", "CVE-2015-3184", "CVE-2018-1312", "CVE-2016-4975", "CVE-2016-8612", "CVE-2014-0226", "CVE-2014-3523", "CVE-2017-15710", "CVE-2017-15715", "CVE-2013-6438", "CVE-2017-7679", "CVE-2019-11040", "CVE-2018-17199", "CVE-2014-8109", "CVE-2017-9798", "CVE-2016-2161", "CVE-2019-11039", "CVE-2019-11038", "CVE-2018-19935", "CVE-2014-0231", "CVE-2013-4352", "CVE-2019-0220", "CVE-2014-0098", "CVE-2018-1283", "CVE-2016-8743"]}
    respString = 'Recon Responses:\nStart over: <br/> <a href="/">Back Home</a>'
    if response['vulns']:
        respString += '<h2>Shodan discovered warnings</h2>'
        respString += '<p>%s</p>' % json.dumps(response['vulns'])


    data = json.dumps(response)
    return respString #'Searching %s and %s on various sources. ' % (companyURL, companyName, data)

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 3000)