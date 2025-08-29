# Coding Agent Protocol

This document outlines how tasks are described and executed by the AXIS Coding Agent. Refer to the [README](../README.md) for project context and [AGENT_INSTRUCTIONS](../AGENT_INSTRUCTIONS.md) for runtime behavior.

## Roles
- **Humans:** create task cards and review pull requests.
- **Agent:** reads the system prompt, executes tasks, and submits PRs.

## Task Cards
Tasks are YAML files describing work items with fields: `id`, `title`, `objective`, `scope`, `constraints`, `inputs`, `outputs`, `acceptance`, `checks`, and `risk`.

## Agent Output JSON
Agent responses follow a JSON schema with keys:
`plan`, `files_to_create_or_edit`, `test_plan`, `commands`, `risk_checks`, and `rollback`.

## Autonomy Levels
- **L0:** analysis only.
- **L1:** code suggestions without committing.
- **L2:** full implementation with tests and PR.

## Workflow (PLAN→TESTS→CODE→SELF-CHECK→PR)
1. Plan actions from the task card.
2. Design and run tests.
3. Apply minimal code changes.
4. Validate results and diffs.
5. Open a pull request with references.

