# Repository Guidelines

## Project Structure & Module Organization
`run.py` is the CLI entry point that delegates to `wgconf.run.runall`. Core logic lives in `wgconf/`: `parseyamlconfig.py` reads YAML templates, `parsewgconfig.py` inspects existing configs, `models.py` holds Pydantic models, and `genkeys.py` wraps key generation. Sample inputs sit next to the README as `interfaces.demo.yaml`, while generated artifacts land in `output/`. Add new modules under `wgconf/` and keep per-feature helpers colocated.

## Build, Test, and Development Commands
Use the uv-managed virtualenv kept in `.venv`. Run `uv venv --seed --clear` to rebuild it and `uv sync` to install dependencies declared in `pyproject.toml`. Generate configs with `uv run run.py interfaces.demo.yaml`; update an existing deployment with `uv run run.py interfaces.yaml output/result.yaml`. If you reuse an activated venv, `python run.py …` is acceptable.

## Coding Style & Naming Conventions
Target Python 3.10+ and mirror the existing four-space indentation. Favor single-quoted strings, explicit imports, and module-level functions in `snake_case`; reserve `PascalCase` for Pydantic models. Keep new helpers pure where possible and stage side effects in the `runall()` workflow. Document non-obvious logic with short docstrings or comments near the code path.

## Testing Guidelines
There is no formal suite yet, so manually validate changes by running the generator against `interfaces.demo.yaml` and inspecting the updated files in `output/`. When adding automated checks, create `tests/test_<module>.py` and exercise them via `uv run pytest`. Capture regressions around YAML merging, key handling, and passive server behavior.

## Commit & Pull Request Guidelines
Git history favors compact, capitalized imperatives (e.g., `Resolve output dir`); follow that tone and keep commits focused. Reference related issues or tickets in the body. Pull requests should outline intent, list reproduction commands, call out config schema changes, and attach anonymized diffs or logs when behavior shifts.

## Security & Configuration Tips
Never commit real Wireguard keys, addresses, or `output/` contents from production. Use sanitized data the way `interfaces.demo.yaml` does. Ensure new code respects file permission expectations in `genkeys.py`, and document any environment variables or secrets that contributors must provide locally.
