# Spanish Word List from RAE

Spanish word list built by scraping the public search interface of the Diccionario de la lengua espanola (RAE) and post-processing the results into sorted text files.

Tags: spanish, rae, dictionary, lexicon, nlp, corpus, scraping, wordlist

> Updated with RAE server in: 2025-02-10

## What this repository contains

The repository stores:

1. Python scripts to query the RAE website.
2. Raw intermediate pickle files under data/raw.
3. Post-processing utilities to produce sorted .txt outputs.
4. Archived snapshots under data/archive.

## Repository layout

```txt
src/                 Python source code
data/raw/            Intermediate pickle files produced by the scraper
data/archive/        Historical snapshots
data/                Final text outputs can be generated here
```

## Requirements

Install the Python dependencies first:

```bash
python -m pip install -r requirements.txt
```

Main runtime dependencies:

1. lxml
2. pyuca

## Main scripts

### src/rae_downloader.py

Downloads one slice of the dictionary and writes a pickle file. It requires --ix, which selects the starting letter index.

Example:

```bash
python src/rae_downloader.py --ix 0
```

Important details:

1. One execution only processes one letter index.
2. Output is written as files like data/raw/allwords_a.pkl by default.
3. --termina switches from the empieza por index to the termina en index used by the RAE site.

### src/post_process.py

Reads all per-letter pickle files, merges them, removes duplicates, sorts them with Spanish collation rules, and writes a final text file.

Example:

```bash
python src/post_process.py --inputfile data/raw/allwords --outputfile data/allwords
```

This generates:

```txt
data/allwords.txt
```

### src/run_full_download.py

Runs the full workflow automatically:

1. Executes src/rae_downloader.py for all letter indexes.
2. Optionally repeats the process with --termina.
3. Executes src/post_process.py.
4. Produces the final consolidated .txt file.

Default usage:

```bash
python src/run_full_download.py
```

With termina mode enabled:

```bash
python src/run_full_download.py --termina
```

Useful options:

```bash
python src/run_full_download.py --from-ix 0 --to-ix 32
python src/run_full_download.py --outfile data/raw/allwords --outputfile data/allwords
```

Notes:

1. Without --termina, the script only queries the empieza por listing.
2. With --termina, it also queries the termina en listing and merges both result sets.
3. The full run can take a long time because it performs many HTTP requests against the RAE site.

## End-to-end workflow

The simplest way to generate the final text file is:

```bash
python src/run_full_download.py
```

At the end of the process you should have:

```txt
data/allwords.txt
```

If you want to maximize coverage, run:

```bash
python src/run_full_download.py --termina
```

## Tests

The test suite covers deterministic logic only. It does not hit the network.

Run all tests with:

```bash
python -m unittest discover -s tests -v
```

Current test coverage includes:

1. Plural generation rules in src/helpers.py.
2. Command orchestration in src/run_full_download.py.

## Limitations

1. The scraper depends on the current HTML structure and query behavior of the RAE website.
2. The full download is network-bound and may take hours.
3. Some optional code paths in the project are still marked as outdated or TODO.
4. This repository scrapes public results pages; review RAE terms and operational limits before running large batches.

## Additional utilities

After generating data/allwords.txt you can also classify the output with the shell scripts in src/.

By length:

```bash
bash src/length.sh
```

By starting letter:

```bash
bash src/starting_letter.sh
```

## Verification checklist

After a large download, double-check at least the following:

1. There are entries starting with accented characters such as a, e, i, o, u with accents.
2. Expected gender and plural variants appear where appropriate.
3. The final file is sorted and has no unexpected duplicates.

## Changelog

2024-10-20:

1. Some variable name typos corrected.
2. Try to get plurals.
3. Verify ababilla.
