#!/usr/bin/python3.6
import requests
import logging
import json
import yaml
import urllib3
import argparse
from getpass import getpass as getpw

#bij gebrek aan beter
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#base_url wordt gemaakt in "def make_url" en gebruikt in alle api calls
base_url = ""
#json_login wordt in "def logon" aangevuld met "Authorization" = "signature" en gebruikt in alle api calls
json_login = {'Content-Type': 'application/json'}
#bij gebrek aan beter wil ik de api_key hergebruiken in een andere functie
api_key = ""
#bij gebrek aan beter wil ik de data verkregen uit uitgevraagde uri hergebruiken in een andere functie
data_uit_uri = ""

def parse_args():
    parser = argparse.ArgumentParser(description=
            "invoervelden")
    parser.add_argument(
            '-u', '--user',
            help ='user, default = pulseapi',
            default='pulseapi',
            type = str
            )
    parser.add_argument(
            '--host',
            help ='host, default = mag-lab',
            default='mag-lab',
            type = str,
            choices=['mag-ams', 'mag-zwl', 'mag-lab']
            )
    args = parser.parse_args()
    return args

def make_url(pulse):
    '''basis url, wordt aangevuld met uri van endpoint in get_data.'''
    global base_url
    base_url = f'https://{pulse}.net.local/api/v1/'
    #print(base_url,"\n")
    return

def log_on(user):
    '''ophalen authentication api_key welke gebruikt word in vervolg calls als username zonder password'''
    global json_login
    global api_key
    password = getpw(f'\n  --> password voor {user}:')
    auth_url = base_url + "auth"
    auth_response = requests.get(auth_url, auth=(user, password), headers=json_login, verify=False)
    data = auth_response.json()
    #print(yaml.dump(data))
    api_key = (data['api_key'])
    #print (api_key,"\n")
    return

def get_data(uri):
    global data_uit_uri
    auth_url =  base_url + uri
    print(auth_url, "\n")
    auth_response = requests.get(auth_url, auth=(api_key, ''), headers=json_login, verify=False)
    data_uit_uri = auth_response.json()
    #print(yaml.dump(data_uit_uri))
    #print("\n")
    return

'''
def log_off():
    auth_url = base_url + "logoff"
    auth_response = requests.post(auth_url, headers=json_login, verify=False)
    print(f' logoff: {str(auth_response)}')
    return
'''
if __name__ == '__main__':
    args = parse_args()
    make_url(args.host)
    log_on(args.user)
    get_data('system/active-users')
    data = data_uit_uri['active-users']['active-user-records']['active-user-record']
    print(type(data))
    for i in range(len(data)):
        print((data[i]['active-user-name']),(data[i]['user-sign-in-time']))     
    #print(yaml.dump(data1))
    #print(f'  >>> file {args.host}.yaml aangemaakt\n\n')
    #log_off()

