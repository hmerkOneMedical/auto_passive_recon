import dns.resolver

Gr = '\033[90m'   # grey
G = '\033[92m'  # green
Y = '\033[93m'  # yellow
B = '\033[94m'  # blue
R = '\033[91m'  # red
W = '\033[0m'   # white
BOLD = '\033[1m'
END = '\033[0m'

def formatInput(promter):
    return raw_input(BOLD + promter+ END + ' \n>>  ')

def formatResponse(title, log = '', unwanted_keys = []):
    print("%s==========================%s" % (Gr, W))
    print("%s%s%s%s%s" % (B, BOLD, title, W, END))
    print(pprint(log, 0, unwanted_keys))

def printBoldSecurity(log):
    print(log.replace('Security', BOLD+'Security'+END).replace('cyber', BOLD+'cyber'+END))

def pprint(log, indent, unwanted_keys):
    tabs = indent*'\t' or ''
    if (isinstance(log, str) or (isinstance(log, int))):
        printBoldSecurity(tabs+str(log))
    elif (isinstance(log, set)):
        pprint(list(log), indent, unwanted_keys)
    elif (isinstance(log,list)):
        try:
            print(tabs + ', '.join(log))
        except:
            for item in log:
                if (isinstance(item, str) or (isinstance(item, int))):
                    print(tabs + str(item))
                else:
                    pprint(item, indent+1, unwanted_keys)
                print('\n')
    elif (isinstance(log, dict)):
        if unwanted_keys:
            for unwanted_key in unwanted_keys: 
                if unwanted_key in log:
                    del log[unwanted_key]

        for key in log.keys():
            if isinstance(log[key], str) or isinstance(log[key], int):
                print(tabs+key+': '+str(log[key]))
            else:
                print(tabs+''+key+':')
                pprint(log[key], indent+1, unwanted_keys)
    elif (isinstance(log, unicode)):
        pprint(log.encode('utf-8'), indent, unwanted_keys)
    else:
        print(str(tabs)+str(log))

def resolveDNS(domain): 
    resolver = dns.resolver.Resolver(); 
    res = resolver.query(domain , "A")
    formatted = set([])
    for item in res:
        formatted.update([str(item)])

    return formatted

def domainsToIPs(domains):
    ipSet = set([])
    for domain in domains:
        try:
            ipMatches = resolveDNS(domain)
            ipSet.update(ipMatches)
        except Exception as e:
            print(e)

    return ipSet