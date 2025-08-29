#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Lint task card YAML files."""

import os
import sys
from typing import List

try:
    import yaml
except ImportError:  # pragma: no cover - guidance for missing dependency
    print("PyYAML is required. Install with `pip install pyyaml`.", file=sys.stderr)
    sys.exit(1)

REQUIRED_FIELDS: List[str] = [
    "id",
    "title",
    "objective",
    "scope",
    "constraints",
    "inputs",
    "outputs",
    "acceptance",
    "checks",
    "risk",
]


def lint(path: str) -> int:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    ok = True
    for field in REQUIRED_FIELDS:
        if field not in data:
            print(f"Missing field: {field}", file=sys.stderr)
            ok = False
    for key in data.keys():
        if key not in REQUIRED_FIELDS:
            print(f"Unknown field: {key}", file=sys.stderr)
            ok = False

    for output in data.get("outputs", []):
        if not os.path.exists(output):
            print(f"Output path does not exist: {output}", file=sys.stderr)
            ok = False

    if ok:
        print(f"{path} OK")
        return 0
    return 1


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python scripts/taskcard_lint.py <task_file>", file=sys.stderr)
        raise SystemExit(1)
    raise SystemExit(lint(sys.argv[1]))


if __name__ == "__main__":
    main()
