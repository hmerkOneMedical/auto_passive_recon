import requests
import yaml

### HOW TO USE:
# import scrape
# scrape.companyBasicInfo(NAME_OF_COMPANY)

headers = {
    'User-Agent': "PostmanRuntime/7.15.0",
    'Accept': "*/*",
    'Cache-Control': "no-cache",
    'Postman-Token': "f4123497-7890-47e1-bcaf-1289756dd65e,d4d95342-4a13-4970-b99d-f272d4fa8ef5",
    'Host': "www.crunchbase.com",
    'cookie': "__cfduid=d49a6d0ab174096bf60ab4584ba9968ad1562790556; cid=rBsAsF0mSpzCugAmV5hDAg==; _pxhd=38a60421661568aff5ac8c606b465cfc50bc2a58ffde727e5f758597799c2977:630c74f1-a351-11e9-8735-a7757449f716",
    'accept-encoding': "gzip, deflate",
    'Connection': "keep-alive",
    'cache-control': "no-cache"
    }


def formatResponse(res):
    companyBasics = (res['overview_company_fields'].values())
    locations = (res['overview_fields']['location_group_identifiers'])
    founded_on = res['overview_fields']['founded_on']['value']
    founders = res['overview_fields']['founder_identifiers']
    online = res['overview_fields2']

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

    return {'company': companyBasics, 'location': location, 'founded_on': founded_on, 'founders': founders, 'online': online}

def companyBasicInfo(name):
    url = 'https://www.crunchbase.com/v4/data/entities/organizations/' + name + \
    '?field_ids=%5B%22identifier%22,%22layout_id%22,%22facet_ids%22,%22title%22,%22short_description%22,%22is_unlocked%22%5D&layout_mode=view'

    try:
        response = requests.request("GET", url, headers=headers)    
        res =  yaml.safe_load(response.text)['cards']

        return formatResponse(res)
    except e:
        return 'Scraping crunchbase failed.'
