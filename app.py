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

    for store_name, store in store_list.items():
        if not hasattr(store, 'pat') or not hasattr(store, 'parser'):
            continue
        if not store.pat.match(url):
            continue
        return store.parse(url)

    return message(code='invalid_url')


if __name__ == '__main__':
    app.run()
