import requests
import yaml

from helpers import *

headers = {
    'User-Agent': 'PostmanRuntime/7.15.0',
    'Accept': '*/*',
    'Cache-Control': 'no-cache',
    'Postman-Token': 'f4123497-7890-47e1-bcaf-1289756dd65e,d4d95342-4a13-4970-b99d-f272d4fa8ef5',
    'Host': 'www.crunchbase.com',
    'cookie': '__cfduid=d49a6d0ab174096bf60ab4584ba9968ad1562790556; cid=rBsAsF0mSpzCugAmV5hDAg==; _pxhd=38a60421661568aff5ac8c606b465cfc50bc2a58ffde727e5f758597799c2977:630c74f1-a351-11e9-8735-a7757449f716',
    'accept-encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'cache-control': 'no-cache'
    }

def conver_count(value):
    try:
        value = int(value)
    except: 
        value = "(+)"
    
    return str(value)

def format_response(res):
    companyBasics = (res['overview_company_fields'].values())
    try:
        locations = (res['overview_fields']['location_group_identifiers'])
    except:
        locations = []
    founded_on = res['overview_fields']['founded_on']['value']
    founders = []
    try: 
        founders = res['overview_fields']['founder_identifiers']
    except:
        print('no founders found')
    online = res['overview_fields2']

    employeeCount = res['overview_fields']['num_employees_enum']
    employeeCount = employeeCount.split('_')
    employeeCount = conver_count(employeeCount[1]) + ' - ' + conver_count(employeeCount[2])

    for b in range(len(companyBasics)):
        if not isinstance(companyBasics[b], str):
            companyBasics[b] = companyBasics[b]['value']

    companyBasics = ', '.join(companyBasics)

    location = ''
    for loc in locations:
        loc = loc['value']
        location += loc + '; '

    for f in range(len(founders)):
        founders[f] = founders[f]['value']

    for s in online:
        if not isinstance(online[s], str):
            online[s] = online[s]['value']

    return {'company': companyBasics, 'location': location, 'founded_on': founded_on, 'founders': founders, 'online': online, 'num_employees': employeeCount}

def company_basic_info(name):
    print(name)
    name = name.replace(' ', '-')
    url = 'https://www.crunchbase.com/v4/data/entities/organizations/' + name + \
    '?field_ids=%5B%22identifier%22,%22layout_id%22,%22facet_ids%22,%22title%22,%22short_description%22,%22is_unlocked%22%5D&layout_mode=view'

    print(url)

    try:
        response = requests.request('GET', url, headers=headers)    
        res =  yaml.safe_load(response.text)['cards']

        return format_response(res)
    except Exception as e:
        print('Scraping crunchbase failed.')
        print(e)
        return None


def run_basics(company_name):
    run = True
    while run:
        basics = (company_basic_info(company_name))
        format_print_response('Basic Company Information (Crunchbase)', basics, [])
        if not basics:
            company_name = formatInput('Update company name to try again:')    
            if len(company_name) == 0:
                run = False
        else:
            run = False
            return basics
