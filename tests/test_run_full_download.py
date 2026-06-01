import sys
import unittest
from pathlib import Path
from unittest.mock import patch


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


import run_full_download


class RunFullDownloadTests(unittest.TestCase):
    def test_runs_default_range_and_post_process(self):
        recorded = []

        def fake_run(command, cwd=None, check=None):
            recorded.append((command, cwd, check))

        with patch.object(sys, "argv", ["run_full_download.py", "--from-ix", "0", "--to-ix", "1"]):
            with patch("subprocess.run", side_effect=fake_run):
                exit_code = run_full_download.main()

        self.assertEqual(exit_code, 0)
        self.assertEqual(len(recorded), 3)
        self.assertIn("rae_downloader.py", recorded[0][0][1])
        self.assertEqual(recorded[0][0][-4:], ["--ix", "0", "--outfile", "data/raw/allwords"])
        self.assertEqual(recorded[1][0][-4:], ["--ix", "1", "--outfile", "data/raw/allwords"])
        self.assertIn("post_process.py", recorded[2][0][1])
        self.assertEqual(recorded[2][0][-4:], ["--inputfile", "data/raw/allwords", "--outputfile", "data/allwords"])

    def test_termina_runs_extra_pass_and_passes_flag_to_post_process(self):
        recorded = []

        def fake_run(command, cwd=None, check=None):
            recorded.append((command, cwd, check))

        argv = [
            "run_full_download.py",
            "--from-ix",
            "0",
            "--to-ix",
            "0",
            "--termina",
        ]
        with patch.object(sys, "argv", argv):
            with patch("subprocess.run", side_effect=fake_run):
                exit_code = run_full_download.main()

        self.assertEqual(exit_code, 0)
        self.assertEqual(len(recorded), 3)
        self.assertEqual(recorded[0][0][-4:], ["--ix", "0", "--outfile", "data/raw/allwords"])
        self.assertEqual(recorded[1][0][-5:], ["--ix", "0", "--termina", "--outfile", "data/raw/allwords_termina"])
        self.assertEqual(recorded[2][0][-5:], ["--inputfile", "data/raw/allwords", "--outputfile", "data/allwords", "--termina"])

    def test_invalid_range_exits(self):
        with patch.object(sys, "argv", ["run_full_download.py", "--from-ix", "3", "--to-ix", "1"]):
            with self.assertRaises(SystemExit):
                run_full_download.main()

    def test_quiet_propagates_to_child_commands(self):
        recorded = []

        def fake_run(command, cwd=None, check=None):
            recorded.append((command, cwd, check))

        argv = ["run_full_download.py", "--from-ix", "0", "--to-ix", "0", "--termina", "--quiet"]
        with patch.object(sys, "argv", argv):
            with patch("subprocess.run", side_effect=fake_run):
                with patch("builtins.print") as mock_print:
                    exit_code = run_full_download.main()

        self.assertEqual(exit_code, 0)
        self.assertEqual(len(recorded), 3)
        self.assertIn("--quiet", recorded[0][0])
        self.assertIn("--quiet", recorded[1][0])
        self.assertIn("--quiet", recorded[2][0])
        mock_print.assert_not_called()


if __name__ == "__main__":
    unittest.main()