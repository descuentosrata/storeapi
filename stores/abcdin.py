import re

from bs4 import BeautifulSoup

from common import get_session, only_numbers

pat = re.compile(r'^(https?://www\.abcdin\.cl/tienda/es/abcdin/[\w\-]+)')


def parse(url):
    with get_session() as s:
        req = s.get(url)

    dom = BeautifulSoup(req.text, 'html.parser')

    normal_price = only_numbers(dom.find(attrs={'name': 'normalPrice'}).get('value').split('.')[0])
    offer_price = only_numbers(dom.find(attrs={'name': 'offerPrice'}).get('value').split('.')[0])
    card_price = only_numbers(dom.find(attrs={'name': 'abcdinPrice'}).get('value').split('.')[0])
    name = dom.find(attrs={'itemprop': 'name'}).get_text().strip()
    image = dom.find(attrs={'itemprop': 'image'}).get('src')

    if offer_price == 0:
        offer_price = normal_price
    if card_price == 0:
        card_price = offer_price

    return dict(
        url=url,
        name=name,
        price=normal_price,
        price_sale=offer_price,
        price_card=card_price,
        image='https://www.abcdin.cl' + image,
        raw=None
    )
