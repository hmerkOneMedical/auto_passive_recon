import requests

def get_subdomains(url):
    url = 'https://api.spyse.com/v1/subdomains?domain=' + url
    response = requests.get(url)
    data = response.json()
    response = []
    
    if 'records' in data:
        for rec in data['records']:
            #print rec['domain']
            response.append(rec['domain'])
            # if ('ip' in rec) and ('domain' in rec):
            #     ips = []
            #     for value in rec['ip']:
            #         ips.append(value['ip'])

            #     response[domain] = {'ips': ips}

    return response

#get_subdomains('onemedical.com')