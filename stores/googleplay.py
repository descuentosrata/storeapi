import json
import re
from json.decoder import JSONDecodeError

from common import get_session, message, find_str

pat = re.compile(r'^(https://play\.google\.com/store/apps/details\?id=[a-zA-Z0-9.-]+)')
name = 'Google Play Store'


def parse(url):
    clean_url = pat.findall(url)[0]
    with get_session() as s:
        data = s.get(clean_url).text

    try:
        lds = json.loads('{"@context"' + find_str(data, '{"@context"', '</script'))
    except JSONDecodeError:
        return message(code='invalid_url')

    price = price_sale = int(lds['offers'][0]['price'])
    try:
        x = find_str(data, 'data:[[null,null,[[[[null,[', ']\n]')
        price = x.split('","')[-1].split('\xa0')[-1][:-1].replace(',', '')
        price = 0 if price == '' else int(price)
    except IndexError:
        pass

    return dict(
        url=clean_url,
        name=lds['name'],
        price=price,
        price_sale=price_sale,
        price_card=price_sale,
        image=lds['image'],
        raw=lds
    )

