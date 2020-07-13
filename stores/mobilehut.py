import re

from common import get_session, message

pat = re.compile(r'^(https://mobilehut\.cl/products/[\w\-]+/?)')
name = 'MobileHUT'


def parse(url):
    clean_url = pat.findall(url)[0]
    with get_session() as s:
        data = s.get(clean_url + '.json').json()

    variants = data['product']['variants']
    if len(variants) == 0:
        return message(code='product_not_found')

    try:
        cheaper = sorted(variants, key=lambda i: int(i['price']))[0]
        price_sale = int(cheaper['price'])
        price = int(cheaper['compare_at_price'] or cheaper['price'])
    except ValueError:
        return message(code='product_not_found')

    return dict(
        url=url,
        name=data['product']['title'],
        price=price,
        price_sale=price_sale,
        price_card=price_sale,
        image=data['product']['image']['src'],
        raw=data
    )
