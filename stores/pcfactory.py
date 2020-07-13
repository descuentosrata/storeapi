import re

from bs4 import BeautifulSoup

from common import get_session, only_numbers

pat = re.compile(r'^(https://(www\.)?pcfactory\.cl/producto/[a-z0-9\-]+)')


def parse(url):
    with get_session() as s:
        req = s.get(url)
    dom = BeautifulSoup(req.text, 'html.parser')

    image = dom.find(class_='slides').find('img')
    i_brand = dom.find('span', attrs={'itemprop': 'brand'})
    i_name = dom.find('span', attrs={'itemprop': 'name'})
    name = f'{i_brand.text} {i_name.text}'

    price_cash = only_numbers(dom.find(class_='ficha_precio_efectivo').find('h2').text)
    price_other = only_numbers(dom.find(class_='ficha_precio_normal').find('h2').text)

    price_ref = dom.find(class_='ficha_precio_referencial')
    price_ref = price_other if not price_ref else only_numbers(price_ref.find('h2').text)

    return dict(
        url=url,
        name=name,
        price=price_ref,
        price_sale=price_cash,
        price_card=price_other,
        image='https://www.pcfactory.cl' + image['src'],
        raw=None
    )
