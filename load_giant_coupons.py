"""Just a quick script to load up on all available coupons."""

import configparser
import datetime
import requests


BASE = 'https://giantfood.com'
class Token(object):
    """Represent response from login."""
    def __init__(self, **kwargs):
        attributes = [
            'scope',
            'access_token',
            'expires_in',
            'refresh_token',
            'token_type'
        ]
        for attr in attributes:
            setattr(self, attr, kwargs.get(attr))
        if self.expires_in:
            now = datetime.datetime.now()
            delta = datetime.timedelta(seconds=self.expires_in)
            self.expires_in = now + delta

def read_config(path):
    """Use configparser to read and output the config."""
    config = configparser.ConfigParser()
    config.read(path)
    return config


def create_session():
    """Create a requests Session with all the headers he need."""
    session = requests.Session()
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.5',
        'Authorization': 'Basic NzJkNTBhZDctNjk4MC00OTQxLWFiNGQtNThkYzM0NjVmMDY5OjczMGUyNzgwMDMxNTkwNWMwYThiYzE0ODRmYTUzM2I2NWM0YWI5Mjc4NzdjZTdiZDYyMzUxODcwMWQ0MDY1ODA=',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0'
    }
    session.headers.update(headers)
    return session


def login(session, username, password, client_id):
    """Login to giantfood.

    Returns:
        token (Token): object represent token data"""
    url = BASE + '/auth/oauth/token'
    params = {
        'grant_type': 'password',
        'username': username,
        'password': password,
        'client_id': client_id
    }
    r = session.post(url, params=params)
    token = Token(**r.json())
    session.headers.update({
        'Authorization': '{type} {token}'.\
            format(type=token.token_type, token=token.access_token)
    })
    return token


def retrieve_coupons(session, account_number):
    """Get a list of all available coupons."""
    url = BASE + '/auth/api/private/synergy/coupons/offers/{account_number}'.\
        format(account_number=account_number)
    params = {
        'numRecords': 1000,
        'pageIndex': 0,  # not expecting more than 1000 coupons
        'categories': '',
        'brandes': '',
        # '_': 1518319698159  # I don't know what this is
    }
    r = session.get(url, params=params)
    return r.json()


def get_coupon_ids(coupons):
    """Given the response of retrieve_coupons, return a list of ids."""
    return [coupon['id'] for coupon in coupons['offers']]


def load_coupon(session, account_number, coupon_id):
    """Make the request to load a given coupon to the given account."""
    url = BASE + '/auth/api/private/synergy/coupons/offers/{account_number}'.\
        format(account_number=account_number)
    params = {'offerNumber': coupon_id}
    req = session.put(url, json=params)


def process_coupons(session, account_number, coupons):
    """Given a list of coupons, go throw and load to account."""
    coupon_ids = get_coupon_ids(coupons)
    for coupon_id in coupon_ids:
        load_coupon(session, account_number, coupon_id)


def main():
    config = read_config('config.ini')
    username = config['Giant']['Username']
    password = config['Giant']['Password']
    # We could make a call to find the account number
    # or we can just copy it from the Giant member card
    account_number = config['Giant']['AccountNumber']
    client_id = config['Giant']['ClientId']
    session = create_session()
    token = login(session, username, password, client_id)
    coupons = retrieve_coupons(session, account_number)
    process_coupons(session, account_number, coupons)
    print('LOADED ' + str(len(coupons.get('offers'))) + ' GIANT COUPONS')


if __name__ == '__main__':
    main()
