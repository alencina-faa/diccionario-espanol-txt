import sys
import types
import unittest
from pathlib import Path


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


if "lxml" not in sys.modules:
    sys.modules["lxml"] = types.SimpleNamespace(etree=object())


from helpers import formar_plural


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


if __name__ == "__main__":
    unittest.main()