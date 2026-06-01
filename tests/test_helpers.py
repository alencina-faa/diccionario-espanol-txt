import sys
import types
import unittest
from pathlib import Path


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


if "lxml" not in sys.modules:
    sys.modules["lxml"] = types.SimpleNamespace(etree=object())


from helpers import extract_conjugacion_forms, formar_plural, has_conjugation, has_page_header_word, is_confirmed_plural


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


if __name__ == "__main__":
    unittest.main()