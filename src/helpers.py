import time

from lxml import etree
from urllib.parse   import quote
from urllib.request import Request, urlopen

"""
Cabeceras para la simulación de un navegador
"""
UA="Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"
url_list_empieza="https://dle.rae.es/{}/?m=31&f={}"
url_list_termina="https://dle.rae.es/{}/?m=32&f={}"
url_detail="https://dle.rae.es/{}"
REQUEST_TIMEOUT_SECONDS = 2
RETRY_ATTEMPTS = 10
RETRY_DELAY_SECONDS = 10

"""
Usamos title por que el contenido en determinadas situaciones cambia:
https://dle.rae.es/abollado?m=31

<a data-cat="FETCH" data-acc="LISTA EMPIEZA POR" data-eti="abollado" title="Ir a la entrada abollado, abollada" href="/abollado">abollado<sup>1</sup>, da</a>
<a data-cat="FETCH" data-acc="LISTA EMPIEZA POR" data-eti="abollado" title="Ir a la entrada abollado" href="/abollado#07jAWsp">abollado<sup>2</sup></a>

"""
to_remove_from_title='Ir a la entrada '

skip = len(to_remove_from_title)


def build_request(url, param, offset=0):
    return Request(url.format(quote(param), offset), headers={'User-Agent': UA})


def get_xtree(url, param, offset=0, urlopen_fn=urlopen, sleep_fn=time.sleep):
    tree = None
    attempt = RETRY_ATTEMPTS
    last_error = None
    while attempt > 0 and tree is None:
        try:
            req = build_request(url, param, offset)
            webpage = urlopen_fn(req, timeout=REQUEST_TIMEOUT_SECONDS)
            htmlparser = etree.HTMLParser()
            tree = etree.parse(webpage, htmlparser)
        except Exception as e:
            last_error = e
            attempt -= 1
            print(str(e))
            if attempt > 0:
                sleep_fn(RETRY_DELAY_SECONDS)

    if tree is None:
        raise RuntimeError(
            f"Failed to fetch RAE page for '{param}' after {RETRY_ATTEMPTS} attempts."
        ) from last_error

    return tree


def extract_conjugacion_forms(tree):
    conjugacion = tree.xpath('//div[@id="conjugacion"]//td//text()')
    conjugacion_clean = ' '.join(conjugacion).replace(', ', ' ').replace(' / ', ' ').split(' ')
    return [conj for conj in conjugacion_clean if conj != '']


def has_conjugation(tree):
    contains_conjugacion = tree.xpath('//*[@id="resultados"]/*/a[@class="e2"]/@title')
    return len(contains_conjugacion) > 0, contains_conjugacion


def has_page_header_word(tree):
    posible_palabra = tree.xpath('//*/h1[@class="c-page-header__title"]/text()')
    return len(posible_palabra) > 0, posible_palabra


def is_confirmed_plural(tree, plural_candidate):
    posible_plural = tree.xpath('//*[@id="resultados"]/div[@class="otras"]/p/text()')
    return len(posible_plural) > 0 and plural_candidate in posible_plural[0]


def try_conjugacion(palabra, dict_dump):
    print("Intentamos conjugar " + palabra)
    tree = get_xtree(url_detail, palabra)
    contains, contains_conjugacion = has_conjugation(tree)
    if contains:
        print("^" * 80)
        print(contains_conjugacion)
        for conj in extract_conjugacion_forms(tree):
            print(conj)
            dict_dump[conj] = conj


def try_me_siento_con_suerte(palabra, dict_dump):
    # RAE por ejemplo al buscar si, devuelve psicolo, psiblabla, etc...
    # esta función prueba la cadena de caracteres en la url, la mayoría dará no pero alguna dará sí. Por ejemplo sí.
    # Ahora mismo sí, sí que aparece por la inclusión de las tildes en el lista inicial.
    # pero puede haber situaciones de palabras que no estén en la lista de resultado de búsqueda y que sean palabras.
    print("Intentamos suerte " + palabra)
    tree = get_xtree(url_detail, palabra)
    contains, posible_palabra = has_page_header_word(tree)
    print(posible_palabra)
    if contains:
        print("Aceptamos:" + palabra)
        dict_dump[palabra] = palabra
    else:
        print("Denegamos:" + palabra)


"""
Revisar bien con las reglas de https://www.rae.es/dpd/plural
"""
def formar_plural(palabra):
    plurales = []
    
    # Si la palabra termina en vocal átona o en -e tónica
    if palabra[-1] in ['a', 'e', 'i', 'o', 'u']:
        plurales.append(palabra + 's')
    
    # Si la palabra termina en -a o -o tónicas
    elif palabra[-1] in ['á', 'ó']:
        if palabra not in ['faralá', 'albalá', 'no']:
            plurales.append(palabra + 's')
        else:
            plurales.append(palabra + 'es')
    
    # Si la palabra termina en -i o -u tónicas
    elif palabra[-1] in ['í', 'ú']:
        plurales.append(palabra + 's')
        plurales.append(palabra + 'es')
    
    # Si la palabra termina en -y precedida de vocal
    elif palabra[-1] == 'y' and len(palabra)>1 and palabra[-2] in ['a', 'e', 'i', 'o', 'u']:
        plurales.append(palabra[:-1] + 'es')
        if palabra in ['gay', 'jersey', 'espray', 'yóquey']:
            plurales.append(palabra[:-1] + 's')
    
    # Si la palabra termina en -s o -x
    elif palabra[-1] in ['s', 'x']:
        if palabra[-2:] in ['ás', 'és', 'ís', 'ós', 'ús'] or palabra[-1] == 'x':
            plurales.append(palabra + 'es')
        else:
            plurales.append(palabra)  # invariable
    
    # Si la palabra termina en -l, -r, -n, -d, -z, -j
    elif palabra[-1] in ['l', 'r', 'n', 'd', 'z', 'j']:
        plurales.append(palabra + 'es')
    
    # Si la palabra termina en consonantes distintas de las anteriores
    elif palabra[-1] not in ['l', 'r', 'n', 'd', 'z', 'j', 's', 'x']:
        plurales.append(palabra + 's')
    
    return plurales

# Ejemplo de uso:
# palabra = "sofá"
# print(f"Formas posibles del plural de '{palabra}': {formar_plural(palabra)}")


def try_plural(palabra, dict_dump):
    print("Intentamos plural " + palabra)
    plural = formar_plural(palabra)
    for pl in plural:
        tree = get_xtree(url_detail, pl)
        if is_confirmed_plural(tree, pl):
            print("Aceptamos:" + pl)
            dict_dump[pl] = pl
        else:
            # Puede ser una palabra: a -> plural as, es una palabra.
            # Aquí la denegamos. La recogeremos como palabra en otra parte del script
            print("Denegamos:" + pl)