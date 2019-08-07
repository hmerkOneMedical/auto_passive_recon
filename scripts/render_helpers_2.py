import os

def company_details(details):
    founder_names = ', '.join(details['founders'])
    online_info = ''
    for det in details['online']:
        online_info += '''<a target="_blank" href="'''+ details['online'][det] +'''">'''+ details['online'][det] +'''</a>'''
        online_info += '<br>'

    return '''
        <div class="card" style="width: 100%; display: inline-block;">
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

def founder_emails_compro(company_name, founder_emails):
    return '''
            <h5 style="display: inline-block; vertical-align:top;">Have
                founder emails been compromised? Visit <a target="_blank"
                    href="https://haveibeenpwned.com">HaveIBeenPwned</a> to
                check ''' + ", ".join(founder_emails) + ''' </h5>'''

def format_single_table_row(domain, index):
    EXPOSED_IP = os.environ.get('NGROK_EXPOSED_IP', '127.0.0.1:5000')
    tool_str = ''
    print(domain)
    if 'builtwith' in domain:
        for tool_type in domain['builtwith']:
            try:
                combinedTools = ', '.join(domain['builtwith'][tool_type])
            except:
                combinedTools = domain['builtwith'][tool_type][0]

            tool_str += tool_type +': '+ combinedTools  + '<br>'

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

def domain_details_inner(subdomains):
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

def linkedin_details_inner(employees, jobs):
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