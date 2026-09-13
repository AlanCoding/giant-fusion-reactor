"""Execute every committed Roman Phase-I notebook without dirtying the tree."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK_DIRECTORY = REPOSITORY_ROOT / "analysis" / "notebooks" / "roman"


def notebook_paths() -> list[Path]:
    return sorted(NOTEBOOK_DIRECTORY.glob("[0-9][0-9]*_*.ipynb"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "notebooks",
        nargs="*",
        help="Optional notebook filenames; the default is every existing Roman notebook.",
    )
    arguments = parser.parse_args()
    paths = (
        [NOTEBOOK_DIRECTORY / name for name in arguments.notebooks]
        if arguments.notebooks
        else notebook_paths()
    )
    missing = [path for path in paths if not path.is_file()]
    if missing:
        parser.error("missing notebook(s): " + ", ".join(path.name for path in missing))

    with tempfile.TemporaryDirectory(prefix="roman-workbook-check-") as temporary:
        output_directory = Path(temporary)
        for index, path in enumerate(paths, start=1):
            print(f"[{index}/{len(paths)}] {path.name}", flush=True)
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "nbconvert",
                    "--to",
                    "notebook",
                    "--execute",
                    "--output-dir",
                    str(output_directory),
                    str(path),
                ],
                cwd=REPOSITORY_ROOT,
                check=False,
            )
            if result.returncode:
                return result.returncode
    print(f"PASS: {len(paths)} Roman notebooks executed from fresh kernels.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
