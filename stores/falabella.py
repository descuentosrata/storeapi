import json
import re

from common import get_session, find_str, message

media_url = 'https://falabella.scene7.com/is/image/Falabella/{}_1?$producto308$&wid=1500&hei=1500&qlt=70'
pat = re.compile(r'^(https?://www\.falabella\.com/falabella-cl/product/[0-9]+/[\w.%\-+:]+/[0-9]+/?)')


def parser(url):
    with get_session() as s:
        req = s.get(url)

    if 'https://schema.org/OutOfStock' in req.text:
        return message(code='out_of_stock')

    try:
        data_json = find_str(req.text, '"variants":', ',"layoutType"')
        data_prod = json.loads(data_json)[0]
    except (json.decoder.JSONDecodeError, TypeError):
        return message(code='invalid_url')

    prices = {i['type']: int(i['price'][0].replace('.', '')) for i in data_prod['prices']}
    price = prices.get('normalPrice', prices.get('internetPrice', 0))
    price_sale = prices.get('internetPrice', price)
    price_card = prices.get('cmrPrice', price_sale)

    return dict(
        url=url,
        name=data_prod['name'],
        price=price,
        price_sale=price_sale,
        price_card=price_card,
        image=media_url.format(data_prod['id']),
        raw=data_prod
    )
