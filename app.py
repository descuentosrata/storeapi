import importlib
from flask import Flask, request

from common import message
import stores

app = Flask(__name__)
store_list = {m: importlib.import_module('stores.'+m, 'stores') for m in stores.__all__}


@app.route('/')
def hello_world():
    url = request.args.get('url', '')
    if not url:
        return message('Hello, rata!')

    for mod_name, store in store_list.items():
        if not all(hasattr(store, i) for i in ['pat', 'parse']):
            continue
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

    return message(code='unsupported_url')


if __name__ == '__main__':
    app.run()
