import re

from common import get_session, find_str, message

api_url = 'https://simple.ripley.cl/api/v3/products?sortBy=availability&partNumbers='
pat = re.compile(r'^(https?://simple\.ripley\.cl/[\w\-]+p?)')
name = 'Ripley'


def parse(url):
    with get_session() as s:
        req = s.get(url)

    ind = 'alternate" href="android-app://cl.baytex.ripley/product/'
    start = req.text.index(ind)
    if start == -1:
        return None

    part = find_str(req.text, ind, '"')
    with get_session() as s:
        data = s.get(api_url + part).json()[0]

    if 'prices' not in data or 'listPrice' not in data['prices']:
        return message(code='out_of_stock')

    return dict(
        url=url,
        name=data['name'],
        price=int(data['prices']['listPrice']),
        price_sale=int(data['prices']['offerPrice']),
        price_card=int(data['prices'].get('cardPrice', data['prices']['offerPrice'])),
        image='https:' + data['fullImage'],
        raw=data
    )
