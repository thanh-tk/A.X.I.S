#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Run a task card locally with optional dry-run."""

import argparse
import json
import pathlib
import sys

try:
    import yaml
except ImportError:  # pragma: no cover
    print("PyYAML is required. Install with `pip install pyyaml`.", file=sys.stderr)
    raise SystemExit(1)

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from scripts.validate_agent_output import validate_agent_output

SYSTEM_PROMPT_PATH = pathlib.Path(__file__).resolve().parent / "SYSTEM_PROMPT.md"


def load_file(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def dry_run(task: dict) -> None:
    sample = {
        "plan": f"Review task {task.get('id', 'unknown')}",
        "files_to_create_or_edit": task.get("outputs", []),
        "test_plan": "noop",
        "commands": ["echo dry-run"],
        "risk_checks": "none",
        "rollback": "",
    }
    validate_agent_output(sample)
    print(json.dumps(sample, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a task card locally")
    parser.add_argument("task", help="Path to task YAML")
    parser.add_argument("--dry-run", action="store_true", help="Emit sample output")
    args = parser.parse_args()

    task_path = pathlib.Path(args.task)
    with task_path.open("r", encoding="utf-8") as f:
        task = yaml.safe_load(f)

    if args.dry_run:
        dry_run(task)
    else:  # pragma: no cover - real agent invocation TBD
        print("Real agent execution not implemented.")


if __name__ == "__main__":
    main()
