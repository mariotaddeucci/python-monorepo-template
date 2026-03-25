---
name: project-commands
description: Build, test, lint, format and autofix commands for this Python monorepo using uv and taskipy
---

## Setup

```bash
uv sync --all-packages   # install / refresh all workspace packages
uv sync                  # install root dev deps only
```

## Run all packages (from repo root)

All root tasks use `scripts/run_task.py` which auto-discovers packages
that define the requested task, runs them with a tqdm progress bar,
and prints a PASS/FAIL summary.

```bash
uv run task test      # pytest in every package that defines 'test'
uv run task lint      # ruff check + pyrefly in every package
uv run task autofix   # ruff check --fix + ruff format in every package
uv run task format    # ruff format in every package
```

## Run a single package (by substring match)

```bash
uv run python scripts/run_task.py test core        # matches my-sample-package-provider-core
uv run python scripts/run_task.py lint app          # matches my-sample-package-provider-app
uv run python scripts/run_task.py format standalone
```

Or directly via uv:

```bash
uv run --directory packages/<name> task test
uv run --directory packages/<name> task lint
uv run --directory packages/<name> task autofix
uv run --directory packages/<name> task format
```

Available package names:

- `my-sample-package`
- `my-sample-package-provider-core`
- `my-sample-package-provider-app`
- `my-sample-package-provider-standalone`

## Documentation

```bash
uv run task docs          # build all package docs, then serve the portal at http://127.0.0.1:8000/
uv run task docs-build    # build all docs (root + packages) into site/

# serve a single package's docs
uv run --directory packages/<name> task docs
```

## Run specific tests

```bash
# single test file
uv run --directory packages/<name> pytest tests/test_models.py

# single test function
uv run --directory packages/<name> pytest tests/test_models.py::test_from_dict

# keyword match across all packages
uv run pytest -k "test_clamp"
```

## Lint commands directly (without taskipy)

```bash
uv run ruff check packages/
uv run ruff format --check packages/
uv run ruff check --fix packages/
uv run pyrefly check packages/<name>/src/
```

## Add / build packages

```bash
uv add --package <pkg> <dep>   # add a dependency to a specific package
uv build --package <pkg>       # build a single package
```

## Adding a new package

1. Create `packages/<new-name>/` with `src/<module>/`, `tests/`, `.python-version`, `README.md`, `pyproject.toml`.
2. Follow the `hatch-vcs` pattern in `pyproject.toml` (see any existing package).
3. Add taskipy tasks (`test`, `lint`, `autofix`, `format`, `docs`) to the package's `pyproject.toml`.
4. Add `mkdocs.yml` (with `INHERIT: ../../mkdocs.base.yml`) and `docs/` directory.
5. Add the module name to `known-first-party` in root `[tool.ruff.lint.isort]`.
6. Add tag pattern to `.github/workflows/publish.yml` `on.push.tags`.
7. Run `uv sync --all-packages`.

Note: root taskipy tasks auto-discover packages — no need to update them manually.

## CI

- `ci.yml`: ruff check, ruff format --check, prek (semgrep + linters),
  pytest on Python 3.11/3.12/3.13.
- `publish.yml`: triggers on `my-sample-package*:*` tags, validates
  branch policy, builds and publishes via PyPI trusted publishing.
