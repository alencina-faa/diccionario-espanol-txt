import os
import pickle
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


class FakeCollator:
    def __init__(self, _path):
        self.path = _path

    def sort_key(self, value):
        return value


fake_pyuca = types.SimpleNamespace(Collator=FakeCollator)
with patch.dict(sys.modules, {"pyuca": fake_pyuca}):
    import post_process


LETTERS = [
    "a", "á", "b", "c", "d", "e", "é", "f", "g", "h", "i", "í", "j", "k", "l", "m",
    "n", "ñ", "o", "ó", "p", "q", "r", "s", "t", "u", "ú", "ü", "v", "w", "x", "y", "z",
]


class PostProcessTests(unittest.TestCase):
    def create_pickle_set(self, base_path, payload_by_letter):
        for letter in LETTERS:
            file_path = Path(f"{base_path}_{letter}.pkl")
            file_path.parent.mkdir(parents=True, exist_ok=True)
            payload = payload_by_letter.get(letter, {})
            with open(file_path, "wb") as handle:
                pickle.dump(payload, handle)

    def run_post_process(self, temp_root, argv):
        previous_cwd = Path.cwd()
        try:
            os.chdir(temp_root)
            exit_code = post_process.main(argv[1:])
        finally:
            os.chdir(previous_cwd)
        self.assertEqual(exit_code, 0)

    def test_generates_sorted_unique_output_from_pickles(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            self.create_pickle_set(
                temp_root / "data" / "raw" / "allwords",
                {
                    "a": {"casa": "casa", "abeja": "abeja"},
                    "b": {"barco": "barco", "casa": "casa"},
                },
            )

            argv = [
                "post_process.py",
                "--inputfile",
                "data/raw/allwords",
                "--outputfile",
                "data/result",
            ]
            self.run_post_process(temp_root, argv)

            output_path = temp_root / "data" / "result.txt"
            self.assertTrue(output_path.exists())
            self.assertEqual(
                output_path.read_text().splitlines(),
                ["abeja", "barco", "casa"],
            )

    def test_termina_mode_merges_relative_termina_pickles(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            self.create_pickle_set(
                temp_root / "data" / "raw" / "allwords",
                {
                    "a": {"abeja": "abeja"},
                },
            )
            self.create_pickle_set(
                temp_root / "data" / "raw" / "allwords_termina",
                {
                    "a": {"mesa": "mesa"},
                    "b": {"abeja": "abeja", "barco": "barco"},
                },
            )

            argv = [
                "post_process.py",
                "--inputfile",
                "data/raw/allwords",
                "--outputfile",
                "data/result_termina",
                "--termina",
                "1",
            ]
            self.run_post_process(temp_root, argv)

            output_path = temp_root / "data" / "result_termina.txt"
            self.assertTrue(output_path.exists())
            self.assertEqual(
                output_path.read_text().splitlines(),
                ["abeja", "barco", "mesa"],
            )


if __name__ == "__main__":
    unittest.main()