import re

from bs4 import BeautifulSoup
from html import unescape

from common import get_session, message, itemschema_ldjson

pat = re.compile(r'^(https?://www\.humblebundle\.com/(store|games)/([\w\-]+))')
single_url = 'humblebundle.com/store'
name = 'Humble Bundle'


def parse(url):
    if single_url in url:
        item_id = pat.match(url).group(3)
        url_api = f'https://www.humblebundle.com/store/api/lookup?products[]={item_id}&request=1'

        with get_session() as s:
            req = s.get(url_api)

        if req.status_code != 200:
            return message(code='invalid_url')

        data = req.json()
        if len(data['result']) == 0:
            return message(code='product_not_found')

        data = data['result'][0]
        return dict(
            url=url,
            name=data['human_name'],
            price=data['full_price']['amount'],
            price_sale=data['current_price']['amount'],
            price_card=data['current_price']['amount'],
            image=data['large_capsule'],
            raw=data
        )
    else:
        with get_session() as s:
            req = s.get(url)

        dom = BeautifulSoup(req.text, 'html.parser')
        isch = itemschema_ldjson(dom)

        if isch is None:
            return message(code='product_not_found')

        return dict(
            url=url,
            name=isch['name'].strip(),
            price=float(isch['offers']['lowPrice']),
            price_sale=float(isch['offers']['highPrice']),
            price_card=float(isch['offers']['highPrice']),
            image=unescape(isch['image']),
            raw=None
        )
