import re
from bs4 import BeautifulSoup

from common import get_session, message, only_numbers

pat = re.compile(r'^(https://www\.cuponatic\.com/descuento/[0-9]+/[0-9a-z]+)')


def parse(url):
    with get_session() as s:
        req = s.get(url)

    dom = BeautifulSoup(req.text, 'html.parser')

    name = dom.select_one('meta[name="og:description"]')
    if name is None:
        return message(code='invalid_url')

    image = dom.select_one('meta[name="og:image"]')['content']
    price_offer = int(dom.select_one('p[itemprop=price]')['content'])
    price_normal = price_offer

    antes_cont = dom.select_one('.detalle-antes span')
    if antes_cont:
        price_offer = only_numbers(dom.select_one('.detalle-antes span').text)

    return dict(
        url=url,
        name=name['content'].strip(),
        price=price_normal,
        price_sale=price_offer,
        price_card=price_offer,
        image=image,
        raw=None
    )
