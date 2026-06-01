import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


if "lxml" not in sys.modules:
    sys.modules["lxml"] = types.SimpleNamespace(etree=types.SimpleNamespace())


import helpers
from helpers import build_request, extract_conjugacion_forms, formar_plural, get_xtree, has_conjugation, has_page_header_word, is_confirmed_plural


class FakeTree:
    def __init__(self, mapping):
        self.mapping = mapping

    def xpath(self, query):
        return self.mapping.get(query, [])


class FormarPluralTests(unittest.TestCase):
    def test_vowel_ending_adds_s(self):
        self.assertEqual(formar_plural("casa"), ["casas"])

    def test_accented_a_adds_s(self):
        self.assertEqual(formar_plural("sofá"), ["sofás"])

    def test_tonic_u_returns_two_candidates(self):
        self.assertEqual(formar_plural("tabú"), ["tabús", "tabúes"])

    def test_s_ending_can_be_invariable(self):
        self.assertEqual(formar_plural("tesis"), ["tesis"])

    def test_x_ending_adds_es(self):
        self.assertEqual(formar_plural("fax"), ["faxes"])

    def test_consonant_ending_adds_es(self):
        self.assertEqual(formar_plural("reloj"), ["relojes"])

    def test_other_consonant_adds_s(self):
        self.assertEqual(formar_plural("robot"), ["robots"])


class HelperExtractionTests(unittest.TestCase):
    def test_extract_conjugacion_forms_flattens_and_filters(self):
        tree = FakeTree(
            {
                '//div[@id="conjugacion"]//td//text()': ["ando", ", ", "ando / iremos", "", "iremos"],
            }
        )

        self.assertEqual(extract_conjugacion_forms(tree), ["ando", "ando", "iremos", "iremos"])

    def test_has_conjugation_detects_titles(self):
        tree = FakeTree({'//*[@id="resultados"]/*/a[@class="e2"]/@title': ["Conjugar verbo"]})

        self.assertEqual(has_conjugation(tree), (True, ["Conjugar verbo"]))

    def test_has_page_header_word_detects_header_presence(self):
        tree = FakeTree({'//*/h1[@class="c-page-header__title"]/text()': ["sí"]})

        self.assertEqual(has_page_header_word(tree), (True, ["sí"]))

    def test_is_confirmed_plural_checks_response_text(self):
        tree = FakeTree({'//*[@id="resultados"]/div[@class="otras"]/p/text()': ["Plural de reloj: relojes"]})

        self.assertTrue(is_confirmed_plural(tree, "relojes"))

    def test_is_confirmed_plural_rejects_missing_candidate(self):
        tree = FakeTree({'//*[@id="resultados"]/div[@class="otras"]/p/text()': ["Plural de reloj: relojes"]})

        self.assertFalse(is_confirmed_plural(tree, "relojs"))


class HelperNetworkTests(unittest.TestCase):
    def test_build_request_quotes_param_and_sets_user_agent(self):
        request = build_request("https://example.test/{}/?f={}", "sí", 20)

        self.assertEqual(request.full_url, "https://example.test/s%C3%AD/?f=20")
        self.assertEqual(request.get_header("User-agent"), helpers.UA)

    def test_get_xtree_retries_and_returns_tree(self):
        calls = []
        sleeps = []
        tree = object()

        def fake_urlopen(_request, timeout):
            calls.append(timeout)
            if len(calls) < 3:
                raise OSError("temporary failure")
            return "response"

        helpers.etree.HTMLParser = lambda: "parser"
        helpers.etree.parse = lambda webpage, parser: tree

        result = get_xtree(
            "https://example.test/{}/?f={}",
            "casa",
            urlopen_fn=fake_urlopen,
            sleep_fn=sleeps.append,
        )

        self.assertIs(result, tree)
        self.assertEqual(calls, [helpers.REQUEST_TIMEOUT_SECONDS] * 3)
        self.assertEqual(sleeps, [helpers.RETRY_DELAY_SECONDS, helpers.RETRY_DELAY_SECONDS])

    def test_get_xtree_raises_clear_error_after_all_retries(self):
        sleeps = []

        def fake_urlopen(_request, timeout):
            raise OSError("network down")

        helpers.etree.HTMLParser = lambda: "parser"
        helpers.etree.parse = lambda webpage, parser: object()

        with self.assertRaisesRegex(RuntimeError, "Failed to fetch RAE page for 'casa'"):
            get_xtree(
                "https://example.test/{}/?f={}",
                "casa",
                urlopen_fn=fake_urlopen,
                sleep_fn=sleeps.append,
            )

        self.assertEqual(len(sleeps), helpers.RETRY_ATTEMPTS - 1)

    def test_get_xtree_quiet_suppresses_retry_logging(self):
        sleeps = []

        def fake_urlopen(_request, timeout):
            raise OSError("silent failure")

        helpers.etree.HTMLParser = lambda: "parser"
        helpers.etree.parse = lambda webpage, parser: object()

        with patch("builtins.print") as mock_print:
            with self.assertRaises(RuntimeError):
                get_xtree(
                    "https://example.test/{}/?f={}",
                    "casa",
                    urlopen_fn=fake_urlopen,
                    sleep_fn=sleeps.append,
                    log_fn=None,
                )

        mock_print.assert_not_called()


if __name__ == "__main__":
    unittest.main()