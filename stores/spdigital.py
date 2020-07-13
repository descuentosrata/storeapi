import re

from bs4 import BeautifulSoup

from common import get_session, only_numbers

pat = re.compile(r'^(https://www\.?spdigital\.cl/products/view/[0-9]+)')
def_image_url = '/img/products/no_image.jpg'
name = 'SPDigital'


def parse(url):
    with get_session() as s:
        content = s.get(url)

    dom = BeautifulSoup(content.content, 'html.parser')
    prod_name = dom.find(id='_name').text.strip()
    image = dom.find(id='_image')['src']
    if image == def_image_url:
        image = 'https://www.spdigital.cl/img/products/no_image.jpg'

    price_cash = only_numbers(dom.find(class_='product-view-cash-price').find('span').text)
    price_other = only_numbers(dom.find(class_='product-view-other-method-price-div').find('span').text)

    prev_price_el = dom.find(class_='product-view-cash-previous-price-value')
    prev_price = price_cash if prev_price_el is None else only_numbers(prev_price_el.text)

    return dict(
        url=url,
        name=prod_name,
        price=prev_price,
        price_sale=price_cash,
        price_card=price_other,
        image=image,
        raw=None
    )
