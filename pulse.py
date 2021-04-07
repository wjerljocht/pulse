#!/usr/bin/python3.6
import argparse
import netrc
import requests
requests.packages.urllib3.disable_warnings()

'''
machine pulseapi
    login pulseapi
    password <password>
'''
username, _, password = netrc.netrc().authenticators('pulseapi')
target = 'mag-lab.net.local'
baseurl = 'https://{target}/api/v1/{{url}}'.format(target=target)
args = None

def get_args():
    '''  '''
    parser = argparse.ArgumentParser(add_help=False, prefix_chars='-+', usage=argparse.SUPPRESS)
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-r', '--report', type=str)
    args = parser.parse_args()
    return args

def set_api_key(session):
    ''' '''
    api_key = session.get(baseurl.format(url='auth')).json()['api_key']
    session.auth = (api_key, '')

def get_session():
    ''' '''
    session = requests.Session()
    session.trust_env = False
    session.verify = False
    session.auth = (username, password)
    set_api_key(session)
    return session

def main():
    ''' '''
    global args
    args = get_args()

    session = get_session()

    roles = session.get(baseurl.format(url='configuration/users/user-roles/'))
    roles = [role['name'] for role in roles.json()['user-role']]

    if args.verbose or not args.report:
        maxlen = len(max(roles, key=len))
        header = f' nr Role'
        seperator = f'--+-+{"-"*(maxlen-1)}'

        print(seperator)
        print(header)
        print(seperator)
        for index, role in enumerate(sorted(roles)):
            print(f'{index:3} {role:{maxlen}}')
        print(seperator)

    if args.report:
        with open(args.report, 'w') as output:
            for role in sorted(roles):
                output.write(f'{role}\n')


if __name__ == '__main__':
    main()
