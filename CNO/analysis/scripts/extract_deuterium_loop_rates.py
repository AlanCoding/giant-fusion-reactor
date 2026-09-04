#!/usr/bin/env python3
"""Extract the deuterium-loop rates from a pinned REACLIB1 snapshot.

The full upstream file is deliberately not committed.  This script verifies
its SHA-256 digest before writing the much smaller, reviewable JSON subset used
by the zero-dimensional fuel-cycle model.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


EXPECTED_SHA256 = "bf5bbc8abe45a17bc413d042e149185738d9ed220a6cc91e1219079e80c4da35"

# REACLIB chapter -> (number of reactants, number of products).
CHAPTER_SHAPES = {
    1: (1, 1),
    2: (1, 2),
    3: (1, 3),
    4: (2, 1),
    5: (2, 2),
    6: (2, 3),
    7: (2, 4),
    8: (3, 1),
    9: (3, 2),
    10: (4, 2),
    11: (1, 4),
}

SELECTED = {
    (("p", "c12"), ("n13",)): "c12-p-g-n13",
    (("he4", "c13"), ("n", "o16")): "c13-a-n-o16",
    (("p", "o16"), ("f17",)): "o16-p-g-f17",
    (("p", "o17"), ("he4", "n14")): "o17-p-a-n14",
    (("p", "n14"), ("o15",)): "n14-p-g-o15",
    (("p", "n15"), ("he4", "c12")): "n15-p-a-c12",
    (("p", "n15"), ("o16",)): "n15-p-g-o16",
    (("p", "o17"), ("f18",)): "o17-p-g-f18",
    (("d", "d"), ("n", "he3")): "d-d-n-he3",
    (("d", "d"), ("p", "t")): "d-d-p-t",
    (("d", "t"), ("n", "he4")): "d-t-n-he4",
    (("n", "p"), ("d",)): "n-p-g-d",
}


def _coefficients(first: str, second: str) -> list[float]:
    fields = [first[index : index + 13] for index in range(0, 52, 13)]
    fields += [second[index : index + 13] for index in range(0, 39, 13)]
    return [float(value) for value in fields]


def parse_reaclib1(text: str) -> list[dict]:
    lines = text.splitlines()
    chapter: int | None = None
    records: list[dict] = []
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        if stripped.isdigit() and int(stripped) in CHAPTER_SHAPES:
            chapter = int(stripped)
            index += 1
            continue
        if chapter is None or index + 2 >= len(lines) or not lines[index][:30].strip():
            index += 1
            continue
        header = lines[index]
        try:
            coefficients = _coefficients(lines[index + 1], lines[index + 2])
            q_mev = float(header[52:64])
        except ValueError:
            index += 1
            continue
        n_reactants, n_products = CHAPTER_SHAPES[chapter]
        # REACLIB reserves columns 1--5 and stores six right-aligned five-byte
        # nuclide fields in columns 6--35.
        nuclides = tuple(header[offset : offset + 5].strip() for offset in range(5, 35, 5))
        nuclides = tuple(value for value in nuclides if value)
        if len(nuclides) != n_reactants + n_products:
            raise ValueError(f"malformed chapter {chapter} record at input line {index + 1}")
        records.append(
            {
                "reactants": nuclides[:n_reactants],
                "products": nuclides[n_reactants:],
                "label": header[43:49].strip(),
                "reverse": "v" in header[49:52],
                "q_mev": q_mev,
                "coefficients": coefficients,
            }
        )
        index += 3
    return records


def extract(source: Path) -> dict:
    content = source.read_bytes()
    digest = hashlib.sha256(content).hexdigest()
    if digest != EXPECTED_SHA256:
        raise ValueError(f"snapshot SHA-256 {digest} does not match pinned {EXPECTED_SHA256}")
    reactions: dict[str, list[dict]] = {reaction_id: [] for reaction_id in SELECTED.values()}
    q_values: dict[str, float] = {}
    for record in parse_reaclib1(content.decode("ascii")):
        key = (tuple(record["reactants"]), tuple(record["products"]))
        reaction_id = SELECTED.get(key)
        if reaction_id is None or record["reverse"]:
            continue
        q_values.setdefault(reaction_id, record["q_mev"])
        if abs(q_values[reaction_id] - record["q_mev"]) > 1e-5:
            raise ValueError(f"inconsistent Q values for {reaction_id}")
        reactions[reaction_id].append(
            {
                "label": record["label"],
                "coefficients": record["coefficients"],
                "t9_min": None,
                "t9_max": None,
            }
        )
    missing = [name for name, entries in reactions.items() if not entries]
    if missing:
        raise ValueError(f"selected reactions absent from snapshot: {', '.join(missing)}")
    return {
        "library": "JINA REACLIB default",
        "upstream_modified": "2026-06-09",
        "retrieved": "2026-09-02",
        "source_url": "https://reaclib.jinaweb.org/difout.php?action=cfreaclib&library=default&rateall=1&cached=&no910=",
        "upstream_sha256": digest,
        "format": "REACLIB1; selected forward entries extracted by analysis/scripts/extract_deuterium_loop_rates.py",
        "rate_range_note": "The snapshot does not declare validity intervals. These rates are screening inputs; high-temperature use needs reaction-specific validation.",
        "q_mev": q_values,
        "reactions": reactions,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="full pinned REACLIB1 snapshot")
    parser.add_argument("output", type=Path, help="selected JSON output")
    args = parser.parse_args()
    data = extract(args.source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, indent=2) + "\n")
    print(f"wrote {len(data['reactions'])} reactions to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
