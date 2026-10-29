# FDE Module 0 runnable starter repository

This learner repository supports **FDE Role, Ethics and Field Safety**. It contains only synthetic scenarios, learner templates, a dependency-free validation utility and 30 supplied baseline tests.

You receive this repository as a ZIP with the Complete Study and Lab Guide. You do **not** create the ZIP yourself. The controlled Assessor and Solutions Guide and the fault catalogue are separate and must not be copied into this repository.

## Safety boundary

- Use only generated data, fictional organisations, `.invalid` domains and documentation IP ranges.
- Do not use customer credentials, exports, screenshots, identities or system details.
- Do not treat a validator result as legal, privacy, safety, security or compliance approval.
- Stop if authority, data provenance, environment scope, evidence integrity or field safety is unclear.

## PowerShell quick start

```powershell
uv python install 3.14.6
uv sync --locked
uv run python .\tools\module0.py baseline
uv run python -m unittest discover -s tests -v
uv run python .\tools\module0.py list-scenarios
uv run python .\tools\module0.py prepare --scenario FDE0-S01 --workspace work\current
```

## Bash or zsh quick start

```bash
uv python install 3.14.6
uv sync --locked
uv run python tools/module0.py baseline
uv run python -m unittest discover -s tests -v
uv run python tools/module0.py list-scenarios
uv run python tools/module0.py prepare --scenario FDE0-S01 --workspace work/current
```

The study guide explains the templates, labs, evidence modes, validation methods and cleanup procedure. A passing machine validation establishes only structural completeness. Assessor observation and specialist decisions remain separate.
