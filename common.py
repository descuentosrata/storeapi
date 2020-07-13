import json
import logging
import re
from json import JSONDecodeError

import requests
from flask import jsonify

logger = logging.getLogger('storeapi')
ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
     'Chrome/74.0.3729.157 Safari/537.36'

# Listado de mensajes y código de estado HTTP mediante un código de mensaje
codes = {
    'missing_url': ('El parámetro "url" es requerido.', 400),
    'unsupported_url': ('Esta URL no es compatible.', 400),
    'invalid_url': ('Página inválida.', 400),
    'out_of_stock': ('Producto sin stock.', 410),
    'product_not_found': ('Producto no encontrado.', 404)
}


def find_str(cont, ini, end):
    """
    Busca una cadena de texto según una cadena inicial y otra final. Extrae el texto que está
    inmediatamente después de la cadena inicial, para buscar la cadena final desde la inicial,
    y devuelve el texto que está entre ellos, sin incluir las cadenas de búsqueda.

    Ejemplo:

    Si cont = `Hola, ¿cómo están todos?, ¿qué tal el día?`, ini = `¿`, end = `?`, el resultado
    será `cómo están todos`.

    :param cont: El contenido donde se buscará.
    :param ini: La cadena de texto inicial.
    :param end: La cadena de texto final.
    :return: El resultado, o None si no se encontró.
    """
    try:
        idx_ini = cont.index(ini) + len(ini)
        idx_end = cont[idx_ini:].index(end) + idx_ini
        return cont[idx_ini:idx_end]
    except ValueError:
        return None


def only_numbers(cont):
    """
    Convierte un str a int filtrando sólo los números del str.
    :param cont: El str objetivo.
    :return: El str filtrado y convertido.
    """
    return int(re.sub('[^0-9]', '', cont))


def get_session():
    """Genera una sesión de Requests con un User-Agent específico."""
    s = requests.Session()
    s.headers.update({'User-Agent': ua})
    return s


def message(msg=None, code=None, status=None):
    """
    Genera una respuesta JSON de Flask de forma estándar para este proyecto.
    :param msg: El mensaje a enviar como el campo "message".
    :param code: El valor del campo código. Si se envía sólo el código, sin los otros parámetros, se buscará
    el mensaje y el código de estado en la lista de códigos "codes" de este módulo.
    :param status: El código de estado HTTP a retornar.
    :return: Una respuesta de Flask en formato JSON.
    """
    if code is None:
        code = 'OK'
    if code in codes:
        msg, status = codes[code]
    elif status is None:
        status = 200

    resp = jsonify({'message': msg, 'code': code, 'error': status != 200})
    resp.status_code = status
    return resp


def itemschema(dom, subsel=None):
    if subsel is not None:
        dom = dom.select_one(subsel)

    prod = dom.select_one('[itemtype="http://schema.org/Product"]')

    if prod is None:
        return None

    defs = {'sku': None, 'name': '', 'price': 0, 'priceCurrency': 'CLP', 'brand': '', 'category': '', 'image': ''}

    for k in defs:
        idom = prod.select_one(f'[itemprop={k}]')
        if not idom:
            continue
        defs[k] = idom.get('content', idom.text).strip()

    return defs


def itemschema_ldjson(dom):
    items = dom.select('script[type="application/ld+json"]')
    if not len(items):
        return None

    data = None
    for item in items:
        try:
            data_cont = json.loads(item.string.strip())
            if '@type' in data_cont and (data_cont['@type'] == 'Product' or data_cont['@type'] == ['Product']):
                data = data_cont
                break
        except JSONDecodeError:
            continue

    return data
