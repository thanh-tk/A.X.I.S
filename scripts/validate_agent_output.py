#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate agent output JSON against schema."""

import json
import pathlib
import sys

try:
    from jsonschema import ValidationError, validate
except ImportError:  # pragma: no cover
    print(
        "jsonschema is required. Install with `pip install jsonschema`.",
        file=sys.stderr,
    )
    sys.exit(1)

SCHEMA_PATH = (
    pathlib.Path(__file__).resolve().parent.parent
    / "schema"
    / "agent_output.schema.json"
)

with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
    SCHEMA = json.load(f)


def validate_agent_output(data: dict) -> None:
    """Raise ValidationError if data is invalid."""
    validate(instance=data, schema=SCHEMA)


def main() -> None:
    if len(sys.argv) != 2:
        print(
            "Usage: python scripts/validate_agent_output.py <json_file>",
            file=sys.stderr,
        )
        raise SystemExit(1)
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        data = json.load(f)
    try:
        validate_agent_output(data)
    except ValidationError as err:  # pragma: no cover
        print(f"Validation error: {err.message}", file=sys.stderr)
        raise SystemExit(1)
    print("Agent output valid")


if __name__ == "__main__":
    main()
