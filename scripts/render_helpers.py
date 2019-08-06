import os

def report_header_html(company_name):
    return '''
    <!DOCTYPE html>
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
        <link
            href="//netdna.bootstrapcdn.com/bootstrap/3.1.0/css/bootstrap.min.css"
            rel="stylesheet"
            id="bootstrap-css"
            />
        <script src="//netdna.bootstrapcdn.com/bootstrap/3.1.0/js/bootstrap.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/1.3.4/jspdf.min.js"></script>
        <link
            href="https://gitcdn.github.io/bootstrap-toggle/2.2.2/css/bootstrap-toggle.min.css"
            rel="stylesheet">
        <script
            src="https://gitcdn.github.io/bootstrap-toggle/2.2.2/js/bootstrap-toggle.min.js"></script>
        <!------ Include the above in your HEAD tag ---------->
        <html>
            <head>
                <title>Automated Report</title>
                <link rel="stylesheet" type="text/css" href="../static/styles.css" />
                <style type="text/css" media="print">
                .dontprint
                { display: none; }
                </style>
            </head>
            <body>
                <hr>
                <div style="width:30px; height: 30px; display: inline-block;
                    vertical-align:top;">
                    <img
                        src="https://www.onemedical.com/static/images/apple-touch-icon-180x180.png"
                        style="max-width:100%;
                        max-height:100%;">
                </div>
                <h1 style="display: inline-block; vertical-align:top;">Passive Recon
                    Report: '''+ company_name +'''</h1>

                <div class="dontprint">
                    <hr>
                    <h4><a target="_blank" href="/">Start Over</a></h4>
                    <h4>To submit report, open the print module, and save as a PDF.<br>
                        Email Security@ and we will get back to you shortly! <br>
                        Note -- please be patient while the full report loads. It may take up to 2 minutes.
                    </h4>
                </div>
                <hr>'''

def report_footer_html():
    return '''</body></html>'''

def details_html(details):
    founder_names = ', '.join(details['founders'])
    online_info = ''
    for det in details['online']:
        online_info += '''<a target="_blank" href="'''+ details['online'][det] +'''">'''+ details['online'][det] +'''</a>'''
        online_info += '<br>'

    return '''
        <div class="card" style="width: 49%; display: inline-block;">
            <div class="card-body">
                <h3 class="card-title">Company Details</h3>
                <ul class="list-group list-group-flush">
                    <li class="list-group-item">Founded Date:
                    ''' + details['founded_on'] + '''</li>
                    <li class="list-group-item">Founders:
                        ''' + founder_names + '''
                    </li>
                    <li class="list-group-item">Private/Public:
                        ''' + details['company'] + '''</li>
                    <li class="list-group-item">Number of Employees:
                        ''' + details['num_employees'] + '''</li>
                    <li class="list-group-item">Headquarters:
                        ''' + details['location'] + '''</li>
                    <li class="list-group-item">Online Presence: <br>
                        ''' + online_info + '''
                    </li>
                </ul>
            </div>
        </div>
        '''

def report_summary_html():
    return '''<!-- Report details -->
        <div class="card" style="width: 49%; display: inline-block;
            vertical-align:top;">
            <div class="card-body">
                <h3 class="card-title">Report Summary</h3>
                <ul class="list-group list-group-flush">
                    <li class="list-group-item" id="toggle_breach_text"
                        style="display:none;">This company has had security
                        breaches in the past. We estimate the breach was
                        significant as a public release was made.</li>
                    <li class="list-group-item" id="toggle_pwned_text"
                        style="display:none;">The founder's email was associated
                        with other security breaches. This can indicate
                        targetting, poor password rotation, or weak passwords.</li>
                    <li class="list-group-item" id="toggle_staff_text"
                        style="display:none;">There appears to be a lack of
                        security engineers. This can present a significant
                        security risk and can pose challenges in uncovering
                        security breaches or timely remediating exploitable
                        flaws in their environment.</li>
                    <li class="list-group-item" id="toggle_vuln_text"
                        style="display:none;">Our automated testing discovered
                        vulnerabilites. See below for details.</li>
                    <li class="list-group-item" id="toggle_high_amt_text"
                        style="display:none;">The vast number of
                        (sub)domains increases security risk.</li>
                    <li class="list-group-item" id="toggle_vuln_text"
                        style="display:block;">Because of the time boxed nature
                        of the reconnaissance and because only publicly
                        available data sources were used, this report is not
                        meant to be indicative of overall security maturity of
                        the company evaluated. Rather, it is meant to be used
                        solely as a potential indicator that can be considered
                        as one part of the overall diligence process.</li>
                </ul>
            </div>
        </div> <hr>'''

def non_automated_checks(company_name, founder_emails):
    return '''<h3 style="page-break-before: always">Non-Automated Checks:</h3>
        <div>
            <h5 style="display: inline-block; width: 50%; vertical-align:top;">Have
                founder emails been compromised? Visit <a target="_blank"
                    href="https://haveibeenpwned.com">HaveIBeenPwned</a> to
                check''' + " ,".join(founder_emails) + ''' </h5>
            <div style="display: inline-block; vertical-align:top; right: 40%;">
                <input
                    type="checkbox"
                    data-toggle="toggle"
                    data-on="Yes"
                    data-off="No"
                    id="toggle_pwned"
                    />
            </div>
            <h5 style="display: inline-block; width: 50%; vertical-align:top;">Have
                there been previous security breaches?</h5>
            <div style="display: inline-block; vertical-align:top; right: 40%;">
                <input
                    type="checkbox"
                    data-toggle="toggle"
                    data-on="Yes"
                    data-off="No"
                    id="toggle_breach"
                    />
            </div>
            <br>
            <div class="dontprint">
                <iframe style="outline:none;width: 500px;height: 500px;"
                    src="https://www.google.com/search?igu=1&ei=&q=''' + company_name + ''' breach"
                    style=></iframe>
            </div>
        </div>
        <hr>

        <script> 
      $(function() {
        $('#toggle_breach').change(function() {
          $('#toggle_breach_text').toggle();
        })
      })
      $(function() {
        $('#toggle_pwned').change(function() {
          $('#toggle_pwned_text').toggle();
        })
      })
      </script>'''

def format_single_table_row(domain, index):
    EXPOSED_IP = os.environ.get('NGROK_EXPOSED_IP', '127.0.0.1:5000')
    tool_str = ''
    print(domain)
    for tool_type in domain['builtwith']:
        tool_str += tool_type +': '+ ' ,'.join(domain['builtwith'][tool_type]) + '<br>'

    vuln_str = ''
    for vuln in domain['vulns']:
        vuln_str += '''<a target="_blank"
                            href="https://nvd.nist.gov/vuln/detail/''' + str(vuln) + '''">
                            ''' + str(vuln) + '''
                        </a><br>'''

    ip_str = '<br>'.join(domain['ips']) if domain['ips'] else ''
    port_str = ''
    for port in domain['ports']:
        port_str += str(port) + '<br>'

    growing_str = '''<tr data-toggle="collapse" data-target="#object-'''+str(index)+'''" class="accordion-toggle">
                    <td><a target="_blank" href="https://'''+domain['url']+'''">
                            '''+domain['url']+'''
                        </a></td>
                    <td>''' + ip_str + '''</td>
                    <td>''' + port_str + '''</td>
                    <td>''' + tool_str + '''</td>
                    <td class="text-error">''' + vuln_str + '''</td>
                </tr>
                <tr>
                <td colspan="6" class="hiddenRow"><div class="accordian-body
                            collapse" id="object-''' + str(index)+ '''"><iframe
                                src="'''+ str(EXPOSED_IP) +'''/frame?url=http://'''+ str(domain['url']) +'''" width="100%" height="200px"
                                style="resize: both;"></iframe>
                        </div> </td>
                    
                </tr>'''

    return growing_str

def domain_html(subdomains):
    print('FORMING INTO AN HTML BLOB')

    tbody_str = ''
    for i in range(len(subdomains)):
        tbody_str += format_single_table_row(subdomains[i], i)

    return '''
            <table class="table table-condensed" style="border-collapse:collapse;">
                <thead>
                    <tr>
                        <th>Subdomain</th>
                        <th>IP Address</th>
                        <th>Ports</th>
                        <th>Built With</th>
                        <th>Vulnerabilities</th>
                    </tr>
                </thead>
                <tbody>
                    ''' + tbody_str + '''
                </tbody>
            </table>
            <hr>'''

def linkedin_details_html(employees, jobs):
    jobs_blob = ''
    for result in jobs:
        jobs_blob += '<tr>'
        jobs_blob += '<td>'+result['title']+'</td>'
        jobs_blob += '<td><a target="_blank" href={{'+result['link']+'}}>LinkedIn</a></td>'
        jobs_blob += '<td>'+result['description']+'</td>'
        jobs_blob += '</tr>'

    employees_blob = ''
    for result in employees:
        employees_blob += '<tr>'
        employees_blob += '<td>'+result['title']+'</td>'
        employees_blob += '<td><a target="_blank" href={{'+result['link']+'}}>LinkedIn</a></td>'
        employees_blob += '<td>'+result['description']+'</td>'
        employees_blob += '</tr>'

    return '''
        <h3>LinkedIn Details</h3>
        <h5 style="display: inline-block; width: 50%;">Information available
            online regarding open positions and current employees, specifically
            with "Cyber" or "Security" in their title. These may all be false
            positives. Do the results indicate a concerning/lack of engineers?</h5>
        <div style="display: inline-block; vertical-align:top; right: 40%;">
            <input
                type="checkbox"
                data-toggle="toggle"
                data-on="Yes"
                data-off="No"
                id="toggle_staff"
                />
        </div>
        <br>
        <script>
        $(function() {
            $('#toggle_staff').change(function() {
            $('#toggle_staff_text').toggle();
            })
        })
        </script>
        <a name="targetname"></a>
        <div class="dontprint">
            <div style="width: 49%; display: inline-block; vertical-align:top;">
                <h3>Hiring</h3>
                <table class="table">
                    <tr>
                        <th scope="col">Title</th>
                        <th scope="col" style="width: 100px;">LinkedIn</th>
                        <th scope="col">Description</th>
                    </tr>'''+ jobs_blob +'''
                </table>
            </div>
            <div style="width: 49%; display: inline-block; vertical-align:top;">
                <h3>Current Employees</h3>
                <table class="table">
                    <tr>
                        <th scope="col">Title</th>
                        <th scope="col" style="width: 100px;">LinkedIn</th>
                        <th scope="col">Description</th>
                    </tr> ''' + employees_blob + '''
                </table>
            </div>
        </div>'''