import sys
from requests import get

def whois(inp):
    result = get('http://api.hackertarget.com/whois/?q=' + inp).text
    return result