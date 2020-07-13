import json
import re

from common import get_session, find_str, message

pat = re.compile(r'^(https?://(www|nuevo)\.jumbo\.cl/[\w\-]+/p)')
url_promos = 'https://apijumboweb.smdigital.cl/proxy/api/v1/json/promotions.json'


def parse(url):
    with get_session() as s:
        req = s.get(url)
        req2 = s.get(url_promos, headers={'x-api-key': 'IuimuMneIKJd3tapno2Ag1c1WcAES97j'}).json()

    try:
        data_json = find_str(req.text, '__renderData = ', ';</script>')
        data = json.loads(json.loads(data_json))
    except json.decoder.JSONDecodeError:
        return message(code='product_not_found')

    del data['menu']
    prod = data['pdp']['product'][0]['items'][0]
    prod_sell = prod['sellers'][0]['commertialOffer']

    price_card = prod_sell['Price']
    prod_id = data['pdp']['product'][0]['productId']
    if prod_id in req2['products']:
        for offer_id in req2['products'][prod_id]:
            if offer_id in req2['promotions']:
                offer = req2['promotions'][offer_id]
                if offer['tcenco'] and offer['value'] < price_card:
                    price_card = offer['value']

    # TODO: dónde está el precio con tarjeta?¿?¿¿
    return dict(
        url=url,
        name=prod['name'],
        price=prod_sell['ListPrice'],
        price_sale=prod_sell['Price'],
        price_card=price_card,
        image=prod['images'][0]['imageUrl'],
        raw=data
    )
