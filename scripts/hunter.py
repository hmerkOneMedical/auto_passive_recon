import os
import requests

HUNTER_API_KEY = os.environ['HUNTER_API_KEY']

def get_work_email(domain, founder_name):
    hunter_url = 'https://api.hunter.io/v2/email-finder?domain={}&full_name={}&api_key={}'.format(domain,founder_name, HUNTER_API_KEY)

    response = requests.get(hunter_url)
    response = response.json() 
    email = response['data']['email']
    if email != None:
        return email
    
    return '[No Email Found]'

#get_work_email('asana.com', 'Dustin Moskovitz')