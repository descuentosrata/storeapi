import re

from bs4 import BeautifulSoup

from common import get_session, itemschema, only_numbers, message

pat = re.compile(r'^(https://(www\.)?linio\.cl/p/[a-z0-9\-]+)')


def parse(url):
    with get_session() as s:
        req = s.get(url)
    dom = BeautifulSoup(req.text, 'html.parser')
    isch = itemschema(dom)

    if not isch['price']:
        return message(code='product_not_found')

    price_main = int(float(isch['price']))
    price_offer = price_main + 0
    price_card = price_main + 0

    price_orig = dom.select_one('.product-price .original-price')
    if price_orig is not None:
        price_main = only_numbers(price_orig.text)

    price_card_cont = dom.select_one('.product-price .price-promotional')
    if price_card_cont is not None:
        price_card = only_numbers(price_card_cont.text)

    return dict(
        url=url,
        name=dom.select_one('meta[itemprop="name"]').get('content'),
        price=price_main,
        price_sale=price_offer,
        price_card=price_card,
        image='https:' + isch['image'],
        raw=None
    )
