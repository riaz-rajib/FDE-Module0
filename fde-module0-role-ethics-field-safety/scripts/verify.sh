#!/usr/bin/env sh
set -eu
uv sync --locked
uv run python tools/module0.py baseline
uv run python -m unittest discover -s tests -v
uv run python -m compileall -q tools tests
printf '%s\n' 'Module 0 baseline verification passed.'
