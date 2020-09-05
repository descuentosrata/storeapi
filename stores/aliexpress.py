import json
import re
from json.decoder import JSONDecodeError

from common import get_session, message, find_str

conf = {'aep_usuc_f': 'isfm=y&site=esp&c_tp=USD&isb=y&region=CL&b_locale=es_ES'}
pat = re.compile(r'^(https://[a-z]{2,3}\.aliexpress\.com/item/[0-9]+\.html)')
name = 'Aliexpress'


def parse(url):
    clean_url = pat.findall(url)[0]
    with get_session() as s:
        data = s.get(clean_url, cookies=conf).text

    try:
        page_data = json.loads(find_str(data, 'data: ', ',\n'))
    except JSONDecodeError:
        return message(code='product_not_found')

    if not page_data or 'priceModule' not in page_data:
        return message(code='product_not_found')

    prices = page_data['priceModule']
    price_offer = price = prices['formatedPrice']
    if 'formatedActivityPrice' in prices:
        price_offer = prices['formatedActivityPrice']

    return dict(
        url=clean_url,
        name=page_data['pageModule']['title'],
        price=price,
        price_sale=price_offer,
        price_card=price_offer,
        image=page_data['pageModule']['imagePath'],
        raw=page_data
    )
