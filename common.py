import logging
from functools import wraps

import requests
from flask import jsonify, request

logger = logging.getLogger('storeapi')
ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
     'Chrome/74.0.3729.157 Safari/537.36'

# Listado de mensajes y código de estado HTTP mediante un código de mensaje
codes = {
    'missing_url': ('El parámetro "url" es requerido.', 400),
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


def get_session():
    """Genera una sesión de Requests con un User-Agent específico."""
    s = requests.Session()
    s.headers.update({'User-Agent': ua})
    return s


def message(msg=None, code=None, status=None):
    if code is None:
        code = 'OK'
    if code in codes:
        msg, status = codes[code]
    elif status is None:
        status = 200

    resp = jsonify({'message': msg, 'code': code, 'error': status != 200})
    resp.status_code = status
    return resp


def validate_request(pat):
    """
    Validador común para los parsers, validando la URL de la tienda
    :param pat: La expresión regular que validará si la URL es correcta.
    :return: El wrapper devuelve un response de Flask con un mensaje si hay algún error, en caso contrario
    devuelve la respuesta original del parser.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            url = request.args.get('url', '')
            if not url:
                return message(code='missing_url')

            if not pat.match(url):
                return message(code='invalid_url')

            return func(url, *args, **kwargs)
        return wrapper
    return decorator
