import json
import re

from common import get_session, find_str, only_numbers

pat = re.compile(r'^(https://www\.(groupon|peixe)\.cl/deals/[0-9a-z\-]+)')


def parse(url):
    with get_session() as s:
        req = s.get(url)

    data = json.loads(find_str(req.text, '__APP_INITIAL_STATE__ = ', '</script>'))
    price = only_numbers(data['deal']['priceSummary']['value']['formattedAmount'])
    price_offer = only_numbers(data['deal']['priceSummary']['price']['formattedAmount'])

    return dict(
        url=url,
        name=data['deal']['title'],
        price=price,
        price_sale=price_offer,
        price_card=price_offer,
        image=data['deal']['largeImageUrl'],
        raw=data
    )
