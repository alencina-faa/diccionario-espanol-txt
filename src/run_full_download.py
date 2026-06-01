#!/usr/bin/env python3

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


TOTAL_LETTERS = 33


def run_command(command: list[str], cwd: Path) -> None:
    print("$", " ".join(command))
    subprocess.run(command, cwd=str(cwd), check=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run rae_downloader.py for all letter indexes and then run post_process.py"
        )
    )
    parser.add_argument(
        "--from-ix",
        type=int,
        default=0,
        help="First index to process (default: 0)",
    )
    parser.add_argument(
        "--to-ix",
        type=int,
        default=TOTAL_LETTERS - 1,
        help=f"Last index to process (default: {TOTAL_LETTERS - 1})",
    )
    parser.add_argument(
        "--outfile",
        default="data/raw/allwords",
        help="Base output path used by rae_downloader.py (default: data/raw/allwords)",
    )
    parser.add_argument(
        "--outputfile",
        default="data/allwords",
        help="Output path (without extension) for post_process.py (default: data/allwords)",
    )
    parser.add_argument(
        "--termina",
        action="store_true",
        help="Also run termina mode and include it in post-processing",
    )

    args = parser.parse_args()

    if args.from_ix < 0 or args.to_ix >= TOTAL_LETTERS or args.from_ix > args.to_ix:
        parser.error(
            f"Invalid range. Use 0 <= from-ix <= to-ix <= {TOTAL_LETTERS - 1}."
        )

    repo_root = Path(__file__).resolve().parents[1]
    src_dir = repo_root / "src"
    python_cmd = sys.executable

    print(
        f"Running downloader for indexes {args.from_ix}..{args.to_ix} "
        f"with outfile '{args.outfile}'"
    )

    for ix in range(args.from_ix, args.to_ix + 1):
        cmd = [
            python_cmd,
            str(src_dir / "rae_downloader.py"),
            "--ix",
            str(ix),
            "--outfile",
            args.outfile,
        ]
        run_command(cmd, cwd=repo_root)

    if args.termina:
        termina_base = f"{args.outfile}_termina"
        print(
            f"Running termina downloader for indexes {args.from_ix}..{args.to_ix} "
            f"with outfile '{termina_base}'"
        )
        for ix in range(args.from_ix, args.to_ix + 1):
            cmd = [
                python_cmd,
                str(src_dir / "rae_downloader.py"),
                "--ix",
                str(ix),
                "--termina",
                "--outfile",
                termina_base,
            ]
            run_command(cmd, cwd=repo_root)

    post_cmd = [
        python_cmd,
        str(src_dir / "post_process.py"),
        "--inputfile",
        args.outfile,
        "--outputfile",
        args.outputfile,
    ]
    if args.termina:
        post_cmd.extend(["--termina", "1"])

    print("Running post-process step")
    run_command(post_cmd, cwd=repo_root)

    print(f"Done. Generated: {args.outputfile}.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
