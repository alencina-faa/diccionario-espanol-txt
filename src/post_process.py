import argparse
import pickle
from pathlib import Path

import pyuca


def default_log(message):
    print(message)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description='RAE Process data.')
    parser.add_argument('--inputfile', metavar='outfile no extension', type=str, default="data/raw/allwords")
    parser.add_argument('--termina', action='store_true')
    parser.add_argument('--quiet', action='store_true', help='Reduce console output')
    parser.add_argument('--outputfile', metavar='outputfile', type=str, default="data/allwords")
    return parser.parse_args(argv)

def save_file(lista, file):
    with open(file, 'w') as f:
        for item in lista:
            f.write(item + '\n')


letras = ['a', 'á', 'b', 'c', 'd', 'e', 'é', 'f', 'g', 'h', 'i', 'í', 'j', 'k', 'l', 'm',
             'n', 'ñ', 'o', 'ó', 'p', 'q', 'r', 's', 't', 'u', 'ú', 'ü', 'v', 'w', 'x', 'y', 'z']


def get_termina_inputfile(args):
    if args.termina:
        return "data/raw/allwords_termina"
    return None


def load_words(inputfile, termina_inputfile=None):
    palabras = []

    for l in letras:
        with open(f"{inputfile}_{l}.pkl", 'rb') as f:
            words = pickle.load(f)
            keys = words.keys()
            palabras += keys
        if termina_inputfile:
            with open(f"{termina_inputfile}_{l}.pkl", 'rb') as f:
                words = pickle.load(f)
                keys = words.keys()
                palabras += keys

    return palabras


def process_words(inputfile, outputfile, termina_inputfile=None, collator_path="src/allkeys.txt"):
    collator = pyuca.Collator(collator_path)
    palabras = load_words(inputfile, termina_inputfile)
    palabras = sorted(list(set(palabras)), key=collator.sort_key)
    save_file(palabras, f"{outputfile}.txt")
    return palabras


def main(argv=None):
    args = parse_args(argv)
    termina_inputfile = get_termina_inputfile(args)
    collator_path = str(Path("src") / "allkeys.txt")
    process_words(args.inputfile, args.outputfile, termina_inputfile, collator_path)
    if not args.quiet:
        default_log(f"Generated: {args.outputfile}.txt")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
