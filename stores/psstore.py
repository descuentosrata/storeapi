import re

from bs4 import BeautifulSoup

from common import get_session, itemschema_ldjson, message

pat = re.compile(r'^(https://store\.playstation\.com/[a-z]{2}-[a-z]{2}/product/[0-9A-Z\-_]+)')
name = 'PlayStation Store'


def parse(url):
    clean_url = pat.findall(url)[0]
    with get_session() as s:
        data = s.get(clean_url).text

    dom = BeautifulSoup(data, features='html.parser')
    lds = itemschema_ldjson(dom)

    current_price = dom.select_one('.price-display__price')
    if not current_price:
        return message(code='product_not_found')
    price_sale = price = current_price.text

    normal_price_dom = dom.select_one('.price-display__strikethrough .price')
    if normal_price_dom:
        price = normal_price_dom.text

    return dict(
        url=clean_url,
        name=lds['name'],
        price=price,
        price_sale=price_sale,
        price_card=price_sale,
        image=lds['image'].split('?')[0],
        raw=lds
    )
