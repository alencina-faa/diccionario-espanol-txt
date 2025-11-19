# List of all spanish words

This project has gained a lot of attention from researchers and application developers. I think that this information should be provided by the RAE organization. Meanwhile you can find the information here.

> Updated with RAE server in: 2025-02-10

## Data layout

```txt
\- src: python source code
\- data
  \- analysis (WorkInProgress)
  \- clean    (WorkInProgress)
  \- meanings (WorkInProgress)
  \- raw
  \- archive
```

## Running

Steps:

1. install requeriments
2. run web scrapper (src/rae_downloader.py) saved as pickle files
3. run post process ( convert to txt, sort, cleaning, etc.)





## Outdated information.

Usage
```
usage: rae_downloader.py [-h] [--conjugaciones] [--skip-conjugaciones]
                         [--outfile outfile]
                         [--outfile outfile]

RAE Downloader.

optional arguments:
  -h, --help            show this help message and exit
  --conjugaciones
  --skip-conjugaciones
  --outfile outfile
```

Words in file has no order and can be duplicades:

```
cat palabras_todas.txt | grep -v '.*-$' | grep -v ^- | sort | uniq > 0_palabras_todas.txt
  --outfile outfile
```

Words in file has no order and can be duplicades:

```
cat palabras_todas.txt | grep -v '.*-$' | grep -v ^- | sort | uniq > 0_palabras_todas.txt
```

### Classify words by their length

The `0_palabras_todas.txt` file is needed.

Inside the `diccionario-espanol-txt` folder and running the `length.sh` file will create the `length` folder with the words classified by its length.

```
bash src/length.sh
```

### Classify words by their first letter

The `0_palabras_todas.txt` file is needed.


Due to the lack of `palabras_todas.txt` file (creating it will last so many hours) the `spliter.sh` file will not work. So this script works with the `0_palabras_todas.txt` file.

Inside the `diccionario-espanol-txt` folder and running the `starting_letter.sh` file will create the `starting_letter` folder with the words classified by the first letter.

```
bash src/starting_letter.sh
```


## Conjugaciones


## Remember

Doble check after download:

- There is words starting by á, é, etc.
- Check plurals: gato, gata, gatos, gatas.

## Changelog

2024-10-20:
- Some variable names typos corrected
- Try to get plurals
- Verifica ababílla
