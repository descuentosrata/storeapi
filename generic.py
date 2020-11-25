import json
from json.decoder import JSONDecodeError

from bs4 import BeautifulSoup
from requests.exceptions import MissingSchema

from common import itemschema_ldjson, get_session, StoreItem, itemschema, find_str, message

vtex_str = 'skuJson_0 = '
rr_str = 'retailrocket.products.post('


def generic_parser(url):
    with get_session() as s:
        try:
            req = s.get(url)
        except MissingSchema:
            return message(code='invalid_url')

        data = req.text
        dom = BeautifulSoup(data, features='html.parser')

    if vtex_str in data:
        return vtex_parser(data, url)

    if rr_str in data:
        result = retailrocket_parser(data, url)
        if result:
            return result

    ldjson = itemschema_ldjson(dom)
    if ldjson:
        return ldjson_parser(url, ldjson)

    isch = itemschema(dom)
    if isch:
        return isch_parser(isch)

    title = image = ''
    ogtitle = dom.select_one('meta[property="og:title"]')
    ogimage = dom.select_one('meta[property="og:image"]')
    if ogtitle:
        title = ogtitle.attrs.get('content', '')
    else:
        domtitle = dom.select_one('title')
        if domtitle:
            title = domtitle.text.strip()

    if ogimage:
        image = ogimage.attrs.get('content', '')

    return StoreItem(
        url=url,
        name=title,
        image=image
    )


def vtex_parser(content, url):
    """Para los sitios basados en el e-commerce Vtex, que exponen los datos del producto de la misma forma"""
    try:
        data = json.loads(find_str(content, vtex_str, ';'))
    except JSONDecodeError:
        return None

    if not data.get('available', False):
        return message(code='out_of_stock')

    sku = data.get('skus', [{}])[0]
    price = sku.get('spotPrice', 0)
    price_sale = sku.get('bestPrice', price)

    if sku.get('listPrice') > 0:
        # En las pruebas, Ilko no usa este campo, pero Casa de la Cerveza sí (precio normal)
        price = sku.get('listPrice', 0)

    # El precio en int aparece como "1000000" en vez de "10000.00", entonces busco en el valor formateado
    # cuántos decimales hay, asumiendo que el separador decimal es una coma
    price_fmt = sku.get('listPriceFormated', '').split(',')
    if len(price_fmt) > 1 and len(price_fmt[-1]) > 0:
        price /= (10 ** len(price_fmt[-1]))
        price_sale /= (10 ** len(price_fmt[-1]))

    return StoreItem(
        url=url,
        name=data.get('name', ''),
        image=sku.get('image', ''),
        price=price,
        price_sale=price_sale,
        price_card=price_sale,
        raw=data
    )


def retailrocket_parser(content, url):
    """Para tiendas basadas en RetailRocket, como AudioMúsica al parecer"""
    try:
        data = json.loads(find_str(content, rr_str, ');'))
    except JSONDecodeError:
        return None

    price = data.get('price', 0)
    return StoreItem(
        url=url,
        name=data.get('name', ''),
        image=data.get('pictureUrl', ''),
        price=price,
        price_sale=price,
        price_card=price,
        raw=data
    )


def ldjson_parser(url, lds):
    price = price_offer = 0
    if 'offers' in lds:
        offers = lds['offers']
        if isinstance(lds['offers'], list):
            offers = offers[0]

        if 'highPrice' in offers and 'lowPrice' in offers:
            price = offers['highPrice']
            price_offer = offers['lowPrice']
        else:
            price = price_offer = offers.get('price', 0)

    return dict(
        url=url,
        name=lds.get('name', ''),
        price=price,
        price_sale=price_offer,
        price_card=price_offer,
        image=lds.get('image', ''),
        raw=lds
    )


def isch_parser(isch):
    price = isch.get('price', 0)
    return StoreItem(
        name=isch['name'],
        image=isch['image'],
        price=price,
        price_sale=price,
        price_card=price
    )


def og_parser(url, data):
    dom = BeautifulSoup(data, features='html.parser')

    title = dom.select_one('meta[property="og:title"]')
    image = dom.select_one('meta[property="og:image"]')

    return StoreItem(
        url=url,
        name='' if title is None else title.get('content', ''),
        image='' if image is None else image.get('content', '')
    )
