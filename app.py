import importlib
from flask import Flask, request

from common import message, StoreItem
import stores
from generic import generic_parser

app = Flask(__name__)
store_list = {m: importlib.import_module('stores.'+m, 'stores') for m in stores.__all__}
store_list = {k: v for k, v in store_list.items() if all(hasattr(v, i) for i in ['pat', 'parse'])}


@app.route('/')
def hello_world():
    url = request.args.get('url', '')

    if not url:
        # Respuesta predeterminada
        return message('Hello, rata!')

    # Iterar por los módulos específicos de tiendas
    for mod_name, store in store_list.items():
        if not store.pat.match(url):
            continue

        item = store.parse(url)
        if not isinstance(item, dict):
            return item

        return {
            'item': item,
            'store_module': mod_name,
            'store_name': getattr(store, 'name', mod_name.title())
        }

    generic_result = generic_parser(url)
    if generic_result is None:
        return message(code='unsupported_url')
    else:
        if isinstance(generic_result, StoreItem):
            generic_result = generic_result.asdict()

        return {
            'item': generic_result,
            'store_module': 'generic',
            'store_name': 'Generic'
        }


if __name__ == '__main__':
    app.run()
