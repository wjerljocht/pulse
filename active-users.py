#!/usr/bin/python3.6
import argparse
import netrc
import collections
import yaml
import requests
requests.packages.urllib3.disable_warnings()

# voorbeel netrc file
'''
cat << EOF >> ~/.netrc
machine pulseapi
    login pulseapi
    password <password>
machine apipulse
    login a<account>
    password <password>
EOF
chmod go-rwx ~/.netrc
'''

# globals
args = None
targets = [
    'mag-lab.net.local',
    'mag-ams.net.local',
    'mag-zwl.net.local',
]
# default target
target = targets[0]
realm = 'AAA'
# username en password ophalen uit netrc file
username, _, password = netrc.netrc().authenticators('apipulse')

# drie spaties tussen de kolommen
space = 3
# list met title-alias combinaties
# key is de waarde uit de API, value is de alias
columns = '''
  - active-user-name: username
  - authentication-realm: realm
  - network-connect-ip: ipaddress
  - network-connect-transport-mode: transport
  - pulse-client-version: version
  - user-roles:
  - user-sign-in-time: time
'''
# omzetten naar dict
columns = yaml.safe_load(columns)

def get_args():
    '''  '''
    parser = argparse.ArgumentParser(add_help=False, prefix_chars='-+', usage=argparse.SUPPRESS)
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-r', '--report', type=str)
    parser.add_argument('-n', '--number', type=int, default=10)
    parser.add_argument('-t', '--target', type=str, default=target, choices=targets)
    args = parser.parse_args()

    return args

# api_key is de 'nieuwe' user
def set_api_key(session):
    ''' '''
    api_key = session.post(baseurl.format(index='realm_auth'), json=dict(realm=realm)).json()['api_key']
    session.auth = (api_key, '')

# creeer een http reauest session
def get_session():
    ''' '''
    session = requests.Session()
    session.trust_env = False
    session.verify = False
    session.auth = (username, password)
    # haal een api key op
    set_api_key(session)

    return session

# 'weg-filteren' admin users
def skip_users(users):
    ''' '''
    return [user for user in users if 'AAA' not in user['authentication-realm']]

# initialiseer column-widths op basis van column title/alias
def get_widths(users):
    widths = collections.defaultdict(int)
    for column in columns:
        for title, alias in column.items():
            widths[title] = len(alias)
    # update column-widths met user-data uit pulse
    for user in users:
        for title, width in widths.items():
            widths[title] = max(len(str(user[title])), width)

    return widths

def display_users(users):
    ''' '''
    widths = get_widths(users)

    # totale breedte van het report nodig voor de eerste separator
    widths_num = [width for width in widths.values()]
    widths_sum, widths_cnt = sum(widths_num), len(widths_num)

    # print seperator
    print(f"{'+'.ljust(widths_sum+space*(widths_cnt-1), '-')}")
    # print target
    print(f'{args.target}')
    # print seperator
    line = list()
    for column in columns:
        for title, alias in column.items():
            line.append(f"{'+'.ljust(widths[title], '-')}{''.ljust(space, '-')}")
    print(''.join(line)[:-space])
    # print titles
    line = list()
    for column in columns:
        for title, alias in column.items():
            line.append(f"{alias:{widths[title]}}{''.ljust(space, ' ')}")
    print(''.join(line)[:-space])
    # print seperator
    line = list()
    for column in columns:
        for title, alias in column.items():
            line.append(f"{'+'.ljust(widths[title], '-')}{''.ljust(space, '-')}")
    print(''.join(line)[:-space])

    # print user-data
    for user in users:
        line = list()
        for title, width in widths.items():
            line.append(f"{str(user[title]):{width}}{''.ljust(space, ' ')}")
        print(''.join(line)[:-space])

def create_report(users):
    ''' '''
    widths = get_widths(users)

    with open(args.report, 'w') as output:
        line = list(['"device"'])
        for column in columns:
            for title, alias in column.items():
                line.append(f'"{alias}"')
        output.write(f'{",".join(line)}\n')
        for user in users:
            line = list([f'"{args.target}"'])
            for item, width in widths.items():
                line.append(f'"{user[item]}"')
            output.write(f'{",".join(line)}\n')

def main():
    ''' '''
    global args
    args = get_args()

    global baseurl
    baseurl = 'https://{target}/api/v1/{{index}}'.format(target=args.target)

    # voeg evnetueel column aliassen toe
    for column in columns:
        for title, alias in column.items():
            if not alias:
                column[title] = title

    # nieuwe http-request sessie inclusief ophalen api-key
    session = get_session()

    # haal een 'args.numver' aantal user objecten op
    users = session.get(baseurl.format(index='system/active-users'), params=dict(number=args.number))
    users = users.json()['active-users']['active-user-records']['active-user-record']
    users = skip_users(users)

    # display users
    if args.verbose or not args.report:
        display_users(users)

    # creeer csv-style report
    if args.report:
        create_report(users)


if __name__ == '__main__':
    main()
