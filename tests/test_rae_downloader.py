import importlib
import pickle
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


class FakeTree:
    def __init__(self, responses):
        self.responses = responses

    def xpath(self, query):
        return self.responses.get(query, [])


class RaeDownloaderTests(unittest.TestCase):
    def import_module_with_helpers(self, fake_get_xtree, fake_try_lucky):
        fake_helpers = types.SimpleNamespace(
            get_xtree=fake_get_xtree,
            try_conjugacion=lambda palabra, data: None,
            try_plural=lambda palabra, data: None,
            try_me_siento_con_suerte=fake_try_lucky,
            url_list_empieza="empieza://{}?f={}",
            url_list_termina="termina://{}?f={}",
            skip=0,
        )

        sys.modules.pop("rae_downloader", None)
        with patch.dict(sys.modules, {"helpers": fake_helpers}):
            return importlib.import_module("rae_downloader")

    def test_main_writes_pickle_for_single_letter_without_pages(self):
        calls = []

        def fake_get_xtree(url, param, offset=0, log_fn=None):
            calls.append((url, param, offset))
            return FakeTree(
                {
                    '//*/*[@class="c-pagination"]/*/text()': [],
                    '//*/article/h3/a/text()': ["abeja", "abeto"],
                    '//*/article/h3/a/i/text()': [],
                }
            )

        lucky_calls = []

        def fake_try_lucky(word, dict_dump, log_fn=None):
            lucky_calls.append(word)
            dict_dump[word] = word

        rae_downloader = self.import_module_with_helpers(fake_get_xtree, fake_try_lucky)

        with tempfile.TemporaryDirectory() as temp_dir:
            outfile = str(Path(temp_dir) / "allwords")
            exit_code = rae_downloader.main(["--ix", "0", "--outfile", outfile])

            self.assertEqual(exit_code, 0)
            self.assertEqual(lucky_calls, ["a"])
            self.assertEqual(calls, [("empieza://{}?f={}", "a", 0)])

            output_path = Path(f"{outfile}_a.pkl")
            self.assertTrue(output_path.exists())
            with open(output_path, "rb") as handle:
                data = pickle.load(handle)

        self.assertEqual(sorted(data.keys()), ["a", "abeja", "abeto"])

    def test_termina_uses_termina_url_list(self):
        calls = []

        def fake_get_xtree(url, param, offset=0, log_fn=None):
            calls.append((url, param, offset))
            return FakeTree(
                {
                    '//*/*[@class="c-pagination"]/*/text()': [],
                    '//*/article/h3/a/text()': [],
                    '//*/article/h3/a/i/text()': [],
                }
            )

        rae_downloader = self.import_module_with_helpers(fake_get_xtree, lambda word, data, log_fn=None: None)

        with tempfile.TemporaryDirectory() as temp_dir:
            outfile = str(Path(temp_dir) / "allwords")
            exit_code = rae_downloader.main(["--ix", "0", "--termina", "--outfile", outfile])

        self.assertEqual(exit_code, 0)
        self.assertEqual(calls, [("termina://{}?f={}", "a", 0)])

    def test_quiet_mode_suppresses_downloader_prints(self):
        def fake_get_xtree(url, param, offset=0, log_fn=None):
            return FakeTree(
                {
                    '//*/*[@class="c-pagination"]/*/text()': [],
                    '//*/article/h3/a/text()': ["abeja"],
                    '//*/article/h3/a/i/text()': [],
                }
            )

        def fake_try_lucky(word, dict_dump, log_fn=None):
            dict_dump[word] = word

        rae_downloader = self.import_module_with_helpers(fake_get_xtree, fake_try_lucky)

        with tempfile.TemporaryDirectory() as temp_dir:
            outfile = str(Path(temp_dir) / "allwords")
            with patch("builtins.print") as mock_print:
                exit_code = rae_downloader.main(["--ix", "0", "--outfile", outfile, "--quiet"])

        self.assertEqual(exit_code, 0)
        mock_print.assert_not_called()


if __name__ == "__main__":
    unittest.main()