import json
import re

from common import get_session, find_str, only_numbers

pat = re.compile(r'^(https?://www\.sodimac\.cl/sodimac-cl/product/[0-9]+/)')
media_url = 'https://sodimac.scene7.com/is/image/SodimacCL/'


def parse(url):
    with get_session() as s:
        req = s.get(url)

    try:
        data_json = find_str(req.text, '__NEXT_DATA__" type="application/json">', '</script>')
        data = json.loads(data_json.strip())
        del data['props']['features']
        del data['props']['footer']
        del data['props']['header']
    except json.decoder.JSONDecodeError:
        return None

    prod = data['props']['pageProps']['productProps']['result']
    prices = {i['type']: only_numbers(i['price']) for i in prod['variants'][0]['price']}
    price = prices['NORMAL']
    price_sale = prices.get('AB', prices.get('INTERNET', price))
    price_card = prices.get('CMR', price_sale)

    return dict(
        url=url,
        name=prod['name'],
        price=price,
        price_sale=price_sale,
        price_card=price_card,
        image=media_url + prod['id'],
        raw=data
    )
