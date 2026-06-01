#!/usr/bin/env python3

# Desarrollado por Jorge Dueñas Lerín

import argparse
import pickle

from helpers import get_xtree, try_me_siento_con_suerte, url_list_empieza, url_list_termina


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description='RAE Downloader.')
    parser.add_argument('--ix', metavar='ix', type=int, required=True, help='Start with this letter index')
    parser.add_argument('--termina', dest='termina', action='store_true')
    parser.add_argument('--outfile', metavar='outfile no extension', type=str, default="data/raw/allwords")
    return parser.parse_args(argv)


letras = ['a', 'á', 'b', 'c', 'd', 'e', 'é', 'f', 'g', 'h', 'i', 'í', 'j', 'k', 'l', 'm',
             'n', 'ñ', 'o', 'ó', 'p', 'q', 'r', 's', 't', 'u', 'ú', 'ü', 'v', 'w', 'x', 'y', 'z']


def get_url_list(termina):
    if termina:
        return url_list_termina
    return url_list_empieza

NITEMS = 20

def procesa(palabras, dict_dump):
    # Se repiten palabras. Cuando por ejemplo aba tiene más de 30 y se exapande
    # abaa, abab, etc... las primeras palabras no aparecen: aba
    numpal = len(palabras)
    for ix, pal in enumerate(palabras):        
        if pal.startswith(","):
            print("Tratada antes", pal)
            continue

        if ix+1 < numpal and palabras[ix+1].startswith(","):
            pal = pal + palabras[ix+1]

        print(pal)
        dict_dump[pal] = pal
        
        """
        This code is comented. It is not update with the last version of the RAE website.
        TODO.
        
        if ", " not in pal_clean:
            pal_list.append(pal_clean)
        else:
            pal_clean = pal_clean.split(", ")
            for pal_clean_multi in pal_clean:
                pal_list.append(pal_clean_multi)
        """
        """
        for pal_ix in pal_list:
            
            #if args.conjugaciones:
            #    try_conjugacion(pal_ix, dict_dump)
            # try_plural(pal_ix, dict_dump)
        """


def run_download(args):
    letras_count = len(letras)
    start = letras[args.ix]
    print(f"Running with {args.ix}/{letras_count}: {start}")
    start_with = [start]
    dict_dump = {}
    url_list = get_url_list(args.termina)

    while len(start_with) != 0:
        palabra_start_with = start_with.pop(0)

        if(palabra_start_with in ['app', 'docs', 'js']): # RAE servers do not like this
            continue

        try_me_siento_con_suerte(palabra_start_with, dict_dump)

        tree = get_xtree(url_list, palabra_start_with)
        pags = tree.xpath('//*/*[@class="c-pagination"]/*/text()')

        res = tree.xpath('//*/article/h3/a/text()')
        procesa(res, dict_dump)

        if pags:
            npags = max([int(x,0) for x in pags if x.isdigit()])
            print("Hay páginas")
            for page in range(npags):
                if page == 0:
                    continue
                print("Página: " + str(page))
                fparam = page*NITEMS

                tree = get_xtree(url_list, palabra_start_with, fparam)
                res = tree.xpath('//*/article/h3/a/text()')
                res = res + tree.xpath('//*/article/h3/a/i/text()')
                procesa(res, dict_dump)

        else:
            print("No hay páginas")

        if pags:
            print("!" * 80)
            print("EXAPEND: " + palabra_start_with)
            expand = [palabra_start_with + l for l in letras]
            start_with = expand + start_with

    with open(f"{args.outfile}_{start}.pkl", "wb") as handle:
        pickle.dump(dict_dump, handle)

    return dict_dump


def main(argv=None):
    args = parse_args(argv)
    run_download(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
