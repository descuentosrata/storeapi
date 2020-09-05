import re

from common import get_session, message

pat = re.compile(r'^(https://store.steampowered.com/app/([0-9]+)/?)')
name = 'Steam'

api_url = 'https://store.steampowered.com/api/appdetails?appids={}&cc=cl'


def parse(url):
    appid = pat.search(url).group(2)
    api = api_url.format(appid)

    with get_session() as s:
        data = s.get(api).json()

    if data.get('success', False):
        return message(code='product_not_found')

    data = data[appid]['data']
    if data['is_free']:
        price = price_sale = 0
    else:
        prices = data['price_overview']
        if not prices['final_formatted']:
            return message(code='out_of_stock')

        price = price_sale = prices['final_formatted'].replace('CLP', '')
        if prices['initial_formatted']:
            price = prices['initial_formatted'].replace('CLP', '')

    return dict(
        url=url,
        name=data['name'],
        price=price,
        price_sale=price_sale,
        price_card=price_sale,
        image=data['header_image'],
        raw=data
    )
