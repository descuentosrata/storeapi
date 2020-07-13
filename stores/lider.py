import re

from bs4 import BeautifulSoup

from common import get_session, itemschema_ldjson, message

pat = re.compile(r'^(https?://(www|get|cyber)\.lider\.cl/(catalogo|supermercado)/product/[\w\-]+/([0-9]+)/?)')
api_base = 'https://buysmart-landing-bff-production.lider.cl/buysmart-checkout-bff/products/' \
           '?sku=SKU&appId=BuySmart&ts=1558232563101'
img_base = 'https://images.lider.cl/wmtcl?source=url[file:/productos/SKUIMAGE]&sink'


def parse(url):
    url_items = list(pat.findall(url)[0])

    if url_items[2] == 'catalogo':
        with get_session() as s:
            data = s.get(api_base.replace('SKU', url_items[3])).json()
        if not len(data):
            return message(code='product_not_found0')

        data = data[0]
        name = data['displayName']
        price = data['price']['BasePriceReference']
        price_sale = data['price']['BasePriceSales'] or price
        price_card = data['price']['BasePriceTLMC'] or price_sale
        image = img_base.replace('SKU', url_items[3]).replace('IMAGE', data['imagesAvailables'][0])
    else:
        with get_session() as s:
            resp = s.get(url)

        data_html = resp.text.replace('/*', '').replace('*/', '')
        dom = BeautifulSoup(data_html, 'html.parser')
        data = itemschema_ldjson(dom)
        name = data['name'] + ' ' + data['brand']
        price = int(data['offers']['highPrice'])
        price_sale = int(data['offers'].get('lowPrice', price))
        price_card = price_sale
        image = data['image']

    return dict(
        url=url,
        name=name,
        price=price,
        price_sale=price_sale,
        price_card=price_card,
        image=image,
        raw=data
    )
