"""Just a quick script to load up on all available coupons."""

import configparser
import datetime
import requests
import random


BASE = 'https://safeway.com'
class Token(object):
    """Represent response from login."""
    def __init__(self, **kwargs):
        attributes = [
            'token',
            'lbcookie',
            'store_id'
        ]
        for attr in attributes:
            setattr(self, attr, kwargs.get(attr))

def read_config(path):
    """Use configparser to read and output the config."""
    config = configparser.ConfigParser()
    config.read(path)
    return config


def create_session():
    """Create a requests Session with all the headers he need."""
    session = requests.Session()
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'DNT': '1',
        'Host': 'www.safeway.com',
        'Origin': 'http://www.safeway.com',
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64; rv:64.0) '
              'Gecko/20100101 Firefox/64.0'),
        'X-Requested-With': 'XMLHttpRequest',
        'X-SWY_API_KEY': 'emjou',
        'X-SWY_BANNER': 'safeway',
        'X-SWY_VERSION': '1.0',
    }
    session.headers.update(headers)
    return session


def login(session, username, password):
    """Login to safeway.

    Returns:
        token (Token): object represent token data"""
    url = BASE + '/iaaw/service/authenticate'
    json_data = {
        'source': 'WEB',
        'rememberMe': False,
        'grant_type': 'password',
        'userId': username,
        'password': password,
    }
    resp = session.post(url, json=json_data)
    token = Token(**resp.json())
    token.store_id = int(resp.json()['userAccount']['storeID'])
    session.headers.update({
        'X-swyConsumerDirectoryPro': token.token,
        'X-swyConsumerlbcookie': token.lbcookie
    })
    return token


def retrieve_coupons(session, store_id):
    """Get a list of all available coupons."""
    url = (BASE + '/abs/pub/web/j4u/api/offers/gallery'
                  '?storeId={}&offerPgm=PD-CC&rand={}'
                  .format(store_id, random.randint(100000, 999999)))
    r = session.get(url)
    return r.json()


def get_coupon_ids(coupons):
    """Given the response of retrieve_coupons, return a list of ids."""
    return [coupon['id'] for coupon in coupons['offers']]


def load_coupon(session, store_id, offer):
    """Make the request to load a given coupon to the given account."""
    url = BASE + '/abs/pub/web/j4u/api/offers/clip?storeId={store_id}'.\
        format(store_id=store_id)
    params = {'items': []}
    for clip_type in ['C', 'L']:
        params['items'].append(
            {
                'clipType': clip_type,
                'itemId': offer['offerId'],
                'itemType': offer['offerPgm'],
            }
        )
    req = session.post(url, json=params)
    return (req.status_code == 200)


def process_coupons(session, store_id, offers):
    """Given a list of coupons, go through and load to account."""
    coupon_load_count = 0
    for offer_type in offers.keys():
        for i,offer in enumerate(offers[offer_type]):
            coupon_type = offer['offerPgm']
            if offer['status'] == 'C':
                continue
            if load_coupon(session, store_id, offer):
                coupon_load_count += 1
    return coupon_load_count


def main():
    config = read_config('config.ini')
    username = config['Safeway']['Username']
    password = config['Safeway']['Password']
    session = create_session()
    token = login(session, username, password)
    coupons = retrieve_coupons(session, token.store_id)
    import pdb; pdb.set_trace()
    coupon_count = process_coupons(session, token.store_id, coupons)
    print('LOADED {coupon_count} SAFEWAY COUPONS'.format(coupon_count=coupon_count))


if __name__ == '__main__':
    main()
