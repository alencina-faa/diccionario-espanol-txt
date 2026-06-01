#!/usr/bin/env python3

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


TOTAL_LETTERS = 33


def default_log(message: str) -> None:
    print(message)


def run_command(command: list[str], cwd: Path, log_fn=default_log) -> None:
    if log_fn is not None:
        log_fn("$ " + " ".join(command))
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
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Reduce console output",
    )

    args = parser.parse_args()

    if args.from_ix < 0 or args.to_ix >= TOTAL_LETTERS or args.from_ix > args.to_ix:
        parser.error(
            f"Invalid range. Use 0 <= from-ix <= to-ix <= {TOTAL_LETTERS - 1}."
        )

    repo_root = Path(__file__).resolve().parents[1]
    src_dir = repo_root / "src"
    python_cmd = sys.executable
    log_fn = None if args.quiet else default_log

    if log_fn is not None:
        log_fn(
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
        if args.quiet:
            cmd.append("--quiet")
        run_command(cmd, cwd=repo_root, log_fn=log_fn)

    if args.termina:
        termina_base = f"{args.outfile}_termina"
        if log_fn is not None:
            log_fn(
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
            if args.quiet:
                cmd.append("--quiet")
            run_command(cmd, cwd=repo_root, log_fn=log_fn)

    post_cmd = [
        python_cmd,
        str(src_dir / "post_process.py"),
        "--inputfile",
        args.outfile,
        "--outputfile",
        args.outputfile,
    ]
    if args.termina:
        post_cmd.append("--termina")
    if args.quiet:
        post_cmd.append("--quiet")

    if log_fn is not None:
        log_fn("Running post-process step")
    run_command(post_cmd, cwd=repo_root, log_fn=log_fn)

    if log_fn is not None:
        log_fn(f"Done. Generated: {args.outputfile}.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
