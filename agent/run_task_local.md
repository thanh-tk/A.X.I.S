# Local Task Runner

Use this helper to preview how a task card would be processed.

## Usage

```bash
python agent/run_task_local.py tasks/TEMPLATE.yaml --dry-run
```

## Notes
- Requires `AGENT_PROTOCOL=true`.
- Dry-run emits sample Agent Output JSON without network calls.
- See [SYSTEM_PROMPT](SYSTEM_PROMPT.md) for agent rules.
