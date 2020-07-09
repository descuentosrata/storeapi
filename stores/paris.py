import html
import json
import re
from json import JSONDecodeError

from common import get_session, find_str, validate_request, message

pat = re.compile(r'^(https?://www\.paris\.cl/.+\.html)')


def parse(url):
    with get_session() as s:
        cont = s.get(url).text

    try:
        cont_json = find_str(cont, '<script type="application/ld+json">', '</script>')
        if not cont_json:
            raise ValueError()
        data = json.loads(cont_json.strip())
    except (JSONDecodeError, ValueError):
        return message(code='invalid_url')

    try:
        price_normal = int(find_str(cont, '"price"><s>$', '<').replace('.', ''))
    except AttributeError:
        price_normal = 0

    prices = sorted([int(i['price']) for i in data['offers']])
    price_sale = price_card = price_normal

    if price_normal != 0:
        if len(prices) > 1:
            price_card, price_sale = prices[0], prices[1]
        elif price_normal != 0 and prices[0] != price_normal:
            price_card = prices[0]
            if 'class="img-tc"' not in cont:
                price_sale = prices[0]
    else:
        price_sale = price_card = price_normal = prices[0]

    return dict(
        url=url,
        name=html.unescape(data['name']),
        price=price_normal,
        price_sale=price_sale,
        price_card=price_card,
        image=data['image'],
        raw=data
    )
