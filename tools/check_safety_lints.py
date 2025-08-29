#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Basic safety lints for the repository."""

import ast
import pathlib
import sys

DISALLOWED_IMPORTS = {"requests", "socket", "subprocess", "httpx", "urllib"}
DISALLOWED_CALLS = {"os.system"}


def check_file(path: pathlib.Path) -> bool:
    with path.open("r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                name = alias.name.split(".")[0]
                if name in DISALLOWED_IMPORTS:
                    print(f"{path}: disallowed import '{name}'", file=sys.stderr)
                    return False
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and isinstance(
                node.func.value, ast.Name
            ):
                fullname = f"{node.func.value.id}.{node.func.attr}"
                if fullname in DISALLOWED_CALLS:
                    print(f"{path}: disallowed call '{fullname}'", file=sys.stderr)
                    return False
    return True


def main() -> None:
    ok = True
    for py_file in pathlib.Path(".").rglob("*.py"):
        if ".git" in py_file.parts:
            continue
        if not check_file(py_file):
            ok = False
    if not ok:
        raise SystemExit(1)
    print("Safety lints passed")


if __name__ == "__main__":
    main()
