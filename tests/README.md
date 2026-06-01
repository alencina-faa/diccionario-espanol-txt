# Tests

This folder contains unit tests for the deterministic parts of the project. The suite avoids network access and does not hit the RAE website.

## Test files

### test_helpers.py

Exercises plural generation rules implemented in src/helpers.py.

Covered behavior:

1. Regular vowel endings.
2. Accented vowel endings.
3. Multiple plural candidates for some tonic endings.
4. Invariable forms.
5. Consonant-based pluralization rules.
6. Extraction helpers for conjugation, page headers, and plural confirmation.
7. HTTP request building and retry behavior in get_xtree().

### test_run_full_download.py

Exercises the command orchestration in src/run_full_download.py.

Covered behavior:

1. Default downloader loop across letter indexes.
2. Extra termina pass when requested.
3. Post-processing invocation.
4. Validation of invalid index ranges.
5. Quiet-mode propagation to child commands.

### test_post_process.py

Executes src/post_process.py against temporary fixture data.

Covered behavior:

1. Merge of per-letter pickle files.
2. Duplicate removal.
3. Sorted text output generation.
4. Merge of termina pickle files when --termina is used.

### test_rae_downloader.py

Exercises src/rae_downloader.py without network access by stubbing helpers.

Covered behavior:

1. Pickle generation for a single letter.
2. URL list selection for empieza and termina modes.
3. Quiet mode without console output.

## Run the tests

From the repository root:

```bash
python -m unittest discover -s tests -v
```

Run a single module:

```bash
python -m unittest tests.test_post_process -v
```
