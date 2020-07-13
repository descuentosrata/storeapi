import json
import re

from bs4 import BeautifulSoup

from common import get_session, find_str, only_numbers

pat = re.compile(r'^(https?://www.tottus.cl/[\w\-]+/p/)')

pat_card = re.compile(r"^\$([0-9.]+) con CMR")
pat_other = re.compile(r"\$([0-9.]+) con Otro Medio")
image_base = 'https://s7d2.scene7.com/is/image/Tottus/'


def parse(url):
    with get_session() as s:
        req = s.get(url)

    try:
        data_json = find_str(req.text, '__NEXT_DATA__" type="application/json">', '</script>')
        data = json.loads(data_json.strip())
        del data['props']['categories']
        del data['props']['settings']
    except json.decoder.JSONDecodeError:
        return None

    prod = data['props']['pageProps']['data']
    price = prod['prices']['regularPrice']
    price_sale = prod['prices'].get('discountPrice', price) or price
    price_card = prod['prices'].get('cmrPrice', price_sale) or price_sale

    return dict(
        url=url,
        name=prod['name'],
        price=price,
        price_sale=price_sale,
        price_card=price_card,
        image=prod['images'][0]['url'],
        raw=data
    )
