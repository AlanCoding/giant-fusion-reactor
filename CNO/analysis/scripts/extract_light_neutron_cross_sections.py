#!/usr/bin/env python3
"""Extract compact MF=3 light-nuclide data from the official ENDF/B-VIII.0 archive."""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
import zipfile
from pathlib import Path

from endf_parserpy import EndfParserCpp


EXPECTED_MD5 = "90c1b1a6653a148f17cbf3c5d1171859"
FILES = {
    "h1": (1, "n-001_H_001.endf"),
    "d": (2, "n-001_H_002.endf"),
    "t": (3, "n-001_H_003.endf"),
    "he3": (3, "n-002_He_003.endf"),
    "he4": (4, "n-002_He_004.endf"),
    "c12": (12, "n-006_C_012.endf"),
    "c13": (13, "n-006_C_013.endf"),
    "n14": (14, "n-007_N_014.endf"),
    "n15": (15, "n-007_N_015.endf"),
    "o16": (16, "n-008_O_016.endf"),
    "o17": (17, "n-008_O_017.endf"),
}
MTS = {"total": 1, "elastic": 2, "capture": 102}


def digest(path: Path) -> str:
    result = hashlib.md5()  # noqa: S324 - verifies a publisher-supplied archive checksum
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def run(archive: Path, output: Path) -> None:
    actual = digest(archive)
    if actual != EXPECTED_MD5:
        raise ValueError(f"ENDF archive MD5 is {actual}, expected {EXPECTED_MD5}")
    parser = EndfParserCpp(ignore_number_mismatch=True)
    result = {
        "library": "ENDF/B-VIII.0 neutron reaction sublibrary",
        "source_url": "https://www.nndc.bnl.gov/endf-b8.0/zips/ENDF-B-VIII.0_neutrons.zip",
        "archive_md5": actual,
        "units": {"energy": "eV", "cross_section": "barn"},
        "notes": [
            "Only MF=3 MT=1,2,102 pointwise arrays are retained.",
            "Nonelastic/removal is evaluated as MT1-MT2; MT102 is retained to identify radiative capture.",
            "Transport treats nonelastic reactions on non-hydrogen species as neutron loss, a conservative approximation.",
        ],
        "nuclides": {},
    }
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        with zipfile.ZipFile(archive) as bundle:
            names = set(bundle.namelist())
            for name, (mass_number, filename) in FILES.items():
                member = f"ENDF-B-VIII.0_neutrons/{filename}"
                if member not in names:
                    raise KeyError(member)
                bundle.extract(member, tmp_path)
                parsed = parser.parsefile(str(tmp_path / member), include=(3,))[3]
                tables = {}
                for label, mt in MTS.items():
                    if mt not in parsed:
                        continue
                    table = parsed[mt]["xstable"]
                    tables[label] = {
                        "energy_eV": table["E"],
                        "cross_section_b": table["xs"],
                    }
                result["nuclides"][name] = {"mass_number": mass_number, "tables": tables}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, separators=(",", ":")))
    print(f"wrote {len(FILES)} light-nuclide evaluations to {output}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.archive, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
