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

Less verbose output:

```bash
python src/rae_downloader.py --ix 0 --quiet
```

Important details:

1. One execution only processes one letter index.
2. Output is written as files like data/raw/allwords_a.pkl by default.
3. --termina switches from the empieza por index to the termina en index used by the RAE site.
4. Old conjugation and plural CLI flags were removed because they were not active in the current scraper implementation.

### src/post_process.py

Reads all per-letter pickle files, merges them, removes duplicates, sorts them with Spanish collation rules, and writes a final text file.

Example:

```bash
python src/post_process.py --inputfile data/raw/allwords --outputfile data/allwords
```

If you also downloaded the termina dataset:

```bash
python src/post_process.py --inputfile data/raw/allwords --outputfile data/allwords --termina
```

Less verbose output:

```bash
python src/post_process.py --inputfile data/raw/allwords --outputfile data/allwords --quiet
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

Quiet mode for long runs:

```bash
python src/run_full_download.py --termina --quiet
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
2. Helper extraction logic in src/helpers.py.
3. Command orchestration in src/run_full_download.py.
4. Post-processing with temporary pickle fixtures.
5. Downloader orchestration without network access.

Recent maintenance work:

1. src/post_process.py and src/rae_downloader.py are now importable and easier to test.
2. src/helpers.py now separates pure extraction logic from HTTP request orchestration.
3. Dead CLI flags and unused imports were removed from the main scripts.
4. HTTP fetching now has explicit retry constants, injectable helpers for testing, and a clear terminal error when retries are exhausted.
5. A --quiet mode is available in the main scripts to reduce console noise during long downloads.

## Limitations

1. The scraper depends on the current HTML structure and query behavior of the RAE website.
2. The full download is network-bound and may take hours.
3. Some optional code paths in the project are still marked as outdated or TODO.
4. This repository scrapes public results pages; review RAE terms and operational limits before running large batches.

## Network behavior

The downloader retries failed page fetches in src/helpers.py with fixed defaults.

Current defaults:

1. 10 attempts per page.
2. 2-second request timeout per HTTP call.
3. 10-second delay between retries.

If all retries fail, the scraper now raises a clear RuntimeError instead of failing later with a less specific NoneType error.

Use --quiet in the CLI entry points if you want to suppress most retry and progress logging during long runs.

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
