import json
import re

from bs4 import BeautifulSoup

from common import get_session, message

pat = re.compile(r'^(https://apps\.apple\.com/[a-z]{2}/app/[a-z0-9\-]+/id[0-9]+)')
name = 'Apple AppStore'


def parse(url):
    clean_url = pat.findall(url)[0]
    with get_session() as s:
        data = s.get(clean_url).text

    dom = BeautifulSoup(data, features='html.parser')
    lds = dom.select_one('script[type="application/ld+json"]')
    if lds is None:
        return message(code='product_not_found')

    lds = json.loads(lds.contents[0])

    price = price_sale = int(lds['offers']['price'])
    return dict(
        url=clean_url,
        name=lds['name'],
        price=price,
        price_sale=price_sale,
        price_card=price_sale,
        image=lds['image'],
        raw=lds
    )
