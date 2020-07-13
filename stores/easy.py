import re

from common import get_session, only_numbers, message

pat = re.compile(r'^(https?://www\.easy\.cl/tienda/producto/([\w\-]+p)/?$)')
api = 'https://www.easy.cl/api//prodeasy*/_search'
req_data = {
    'query': {'bool': {
        'minimum_should_match': 1,
        'should': [{'term': {'url.keyword': ''}}, {'term': {'children.url.keyword': ''}}]
     }}
}


def parse(url):
    part_url = list(pat.findall(url)[0])[1]

    search_data = req_data.copy()
    search_data['query']['bool']['should'][0]['term']['url.keyword'] = part_url
    search_data['query']['bool']['should'][1]['term']['children.url.keyword'] = part_url

    with get_session() as s:
        data = s.post(api, json=search_data).json()
    if len(data['hits']['hits']) == 0:
        return message(code='invalid_url')

    prod = data['hits']['hits'][0]['_source']
    price = only_numbers(prod['children'][0]['price'])
    price_sale = prod['price_internet']
    price_card = prod['price_tc'] or price_sale

    return dict(
        url=url,
        name=prod['name'].strip(),
        price=price,
        price_sale=price_sale,
        price_card=price_card,
        image=prod['fullImage'],
        raw=data
    )
