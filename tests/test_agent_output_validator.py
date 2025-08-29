# SPDX-License-Identifier: MIT
"""Tests for agent output validator."""

import pathlib
import sys

import pytest
from jsonschema import ValidationError

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from scripts.validate_agent_output import validate_agent_output


def test_valid_agent_output():
    data = {
        "plan": "do things",
        "files_to_create_or_edit": ["file.txt"],
        "test_plan": "run tests",
        "commands": ["echo hi"],
        "risk_checks": "none",
        "rollback": "git reset --hard",
    }
    validate_agent_output(data)


def test_invalid_agent_output_missing_field():
    data = {"plan": "do things", "files_to_create_or_edit": []}
    with pytest.raises(ValidationError):
        validate_agent_output(data)
