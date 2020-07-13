import re

from common import get_session, message

api_base = 'https://www.hites.com/on/demandware.store/Sites-HITES-Site/default/Product-Variation?pid='
default_img = 'https://checkout.hites.com/wcsstore/HitesSAS/images/NoImageIcon.jpg'
pat = re.compile(r'^https?://www\.hites\.com/[\w\-.]+-([0-9]+)\.html')


def parse(url):
    pid = pat.search(url).groups()
    if not pid:
        return message(code='invalid_url')

    with get_session() as s:
        req = s.get(api_base + pid[0])

    if req.status_code != 200:
        return message(code='invalid_url')

    try:
        data = req.json()
        if 'product' not in data or 'price' not in data['product'] or 'list' not in data['product']['price']:
            raise ValueError()
    except ValueError:
        return message(code='invalid_url')

    product = data['product']
    price = price_sale = price_card = product['price']['list']['value']

    d_price_sales = product['price'].get('sales', None)
    if isinstance(d_price_sales, dict) and 'value' in d_price_sales and d_price_sales['value']:
        price_sale = d_price_sales['value']

    d_price_card = product['price'].get('hites', None)
    if isinstance(d_price_card, dict) and 'value' in d_price_card and d_price_card['value']:
        price_card = d_price_card['value']
    elif price_sale:
        price_card = price_sale

    image_url = default_img
    if 'images' in product and 'large' in product['images'] and isinstance(product['images']['large'], list) \
       and len(product['images']['large']) > 0:
        image_url = product['images']['large'][0]['absURL']

    return dict(
        url=url,
        name=product['productName'],
        price=price,
        price_sale=price_sale,
        price_card=price_card,
        image=image_url,
        raw=data
    )
