#!/usr/bin/env python3
"""Replace unresolved Pb-208 MF=3 backgrounds with NNDC processed arrays.

The ENDF evaluation archive stores low-energy Pb-208 resonance parameters in
MF=2.  Reading MF=3 alone therefore produces an invalid near-zero low-energy
cross section.  NNDC's ENDF API publishes the resonance-reconstructed 293.15 K
arrays.  This small build step merges downloaded API responses into the
compact transport card.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IDS = {
    "total": 109038,
    "elastic": 108797,
    "capture": 109019,
}
API_ROOT = "https://www.nndc.bnl.gov/endf-api/cross-sections"


def read_table(path: Path, expected_id: int) -> dict[str, list[float]]:
    raw = json.loads(path.read_text())
    if raw["id"] != expected_id or raw["temperature"] != 293.15:
        raise ValueError(f"unexpected NNDC cross-section record in {path}")
    axes = {axis["label"]: axis for axis in raw["axes"]}
    return {
        "energy_eV": axes["energy_in"]["values"],
        "cross_section_b": axes["crossSection"]["values"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--total", type=Path, required=True)
    parser.add_argument("--elastic", type=Path, required=True)
    parser.add_argument("--capture", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    card = json.loads(args.base.read_text())
    sources = {"total": args.total, "elastic": args.elastic, "capture": args.capture}
    card["nuclides"]["pb208"] = {
        "mass_number": 208,
        "tables": {
            label: read_table(path, IDS[label])
            for label, path in sources.items()
        },
    }
    card["notes"].extend(
        [
            "Pb-208 uses NNDC ENDF API resonance-reconstructed 293.15 K arrays, not unreconstructed MF=3 backgrounds.",
            "Pb-208 API records: "
            + ", ".join(f"{label}={API_ROOT}/{record_id}" for label, record_id in IDS.items()),
        ]
    )
    args.output.write_text(json.dumps(card, separators=(",", ":")))
    print(f"merged processed Pb-208 tables into {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
