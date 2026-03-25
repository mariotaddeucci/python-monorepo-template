# AGENTS.md

Guidelines for agentic coding agents working in this Python monorepo.

---

## Repository structure

```
python-monorepo-template/
├── pyproject.toml                        # workspace root: ruff, pytest, taskipy
├── uv.lock
├── scripts/run_task.py                   # legacy dispatcher (kept for reference)
└── packages/
    ├── my-sample-package/                # proxy package — re-exports all providers
    ├── my-sample-package-provider-core/  # Python >=3.11, module: core
    ├── my-sample-package-provider-app/   # Python >=3.12, module: app
    └── my-sample-package-provider-standalone/ # Python >=3.13, module: standalone
```

Each package lives under `packages/<name>/` and follows the layout:
- `src/<module>/` — importable source
- `tests/` — pytest test files
- `pyproject.toml` — package metadata + taskipy tasks
- `.python-version` — minimum Python for that package
- `README.md`

---

## Toolchain

**Always use `uv`** for everything — never `pip`, `python -m pip`, or `poetry`.

```bash
uv sync --all-packages          # install / refresh all workspace packages
uv sync                         # install root dev deps only
uv run <cmd>                    # run a command inside the venv
uv add --package <pkg> <dep>    # add a dependency to a specific package
uv build --package <pkg>        # build a single package
```

---

## Build / lint / test commands

### Run all packages (from repo root)

```bash
uv run task test      # run tests in all 4 packages
uv run task lint      # ruff check + pyrefly check in all packages
uv run task autofix   # ruff check --fix + ruff format in all packages
uv run task format    # ruff format in all packages
```

### Run a single package

```bash
uv run --directory packages/my-sample-package-provider-core task test
uv run --directory packages/my-sample-package-provider-app  task lint
uv run --directory packages/my-sample-package               task autofix
```

### Run a single test file or test function

```bash
# single test file
uv run --directory packages/my-sample-package-provider-core pytest tests/test_models.py

# single test function (most common for targeted debugging)
uv run --directory packages/my-sample-package-provider-core pytest tests/test_models.py::test_from_dict

# keyword match across all packages
uv run pytest -k "test_clamp"
```

### Lint commands directly (without taskipy)

```bash
uv run ruff check packages/
uv run ruff format --check packages/
uv run ruff check --fix packages/
uv run pyrefly check packages/<name>/src/
```

---

## Adding a new package

1. Create `packages/<new-name>/` with `src/<module>/`, `tests/`, `.python-version`, `README.md`, `pyproject.toml`.
2. Follow the `hatch-vcs` pattern in `pyproject.toml` (see any existing package).
3. Add the package's taskipy tasks (`test`, `lint`, `autofix`, `format`).
4. Append the package to all four root taskipy tasks in the root `pyproject.toml`.
5. Add the module name to `known-first-party` in root `[tool.ruff.lint.isort]`.
6. Add tag pattern to `.github/workflows/publish.yml` `on.push.tags`.
7. Run `uv sync --all-packages`.

---

## Code style

### Formatting

- Line length: **120 characters** (`ruff` enforcer).
- Indentation: **spaces** (4 per level).
- Quotes: **double quotes** (`"`).
- Configured in root `pyproject.toml` under `[tool.ruff.format]`.

### Imports

Order (enforced by ruff isort):
1. Standard library
2. Third-party
3. First-party (`core`, `app`, `standalone`, `my_sample_package`)

- One import per line for `from … import` with multiple names — or group tightly if few.
- Use `from __future__ import annotations` at the top of files that use forward references or `|` union syntax with Python <3.10 compatibility in mind.
- Optional dependencies must be guarded with `try/except ImportError`:

```python
try:
    from core.utils import process_data
    _CORE_AVAILABLE = True
except ImportError:
    _CORE_AVAILABLE = False
```

### Type annotations

- All public functions and methods must have **full type annotations** on parameters and return values.
- Use built-in generics (`list[str]`, `dict[str, int]`) — not `typing.List` / `typing.Dict` (requires Python >=3.9; `from __future__ import annotations` enables this on 3.8 too).
- Use `typing.Any` for genuinely unknown types; avoid overusing it.
- `-> None` is required on `__init__` and other void methods.

### Naming conventions

| Kind | Convention | Example |
|---|---|---|
| Modules / packages | `snake_case` | `core/utils.py` |
| Classes | `PascalCase` | `DataModel`, `Pipeline` |
| Functions / methods | `snake_case` | `format_message`, `filter_by_tag` |
| Constants / module-level flags | `UPPER_SNAKE` | `_CORE_AVAILABLE` |
| Private helpers | leading `_` | `_suggest_extra`, `_ATTR_MAP` |

### Docstrings

Use Google-style docstrings for all public modules, classes, and functions:

```python
def clamp(value: float, min_value: float, max_value: float) -> float:
    """Clamp a value between min and max.

    Args:
        value: The value to clamp.
        min_value: Lower bound (inclusive).
        max_value: Upper bound (inclusive).

    Returns:
        The clamped value.

    Example:
        >>> clamp(15, 0, 10)
        10
    """
```

Private/internal helpers do not require full docstrings, but a one-liner is encouraged.

### Error handling

- Raise specific built-in exceptions (`ValueError`, `RuntimeError`, `AttributeError`, `TypeError`) with descriptive messages.
- Include the package name and install hint in user-facing errors raised when an optional dep is missing:
  ```python
  raise RuntimeError("Tag filtering requires the 'core' extra: pip install app[core]")
  ```
- Never use bare `except:` — always catch a specific exception type.
- Do not use `assert False` — raise `AssertionError(...)` explicitly or use `pytest.raises` in tests.

---

## Tests

- Test files: `test_*.py` inside `tests/` of each package.
- **Tests must be functions**, never classes (`def test_*`, not `class TestFoo`).
- Fixtures are defined with `@pytest.fixture` in the same test file (or a `conftest.py` if shared).
- Use `pytest.raises` for expected exceptions — never `try/except` + `assert False`.
- Test names should read as a sentence describing the expected behaviour:
  ```python
  def test_clamp_above_max():
  def test_pipeline_filter_tag_without_core_raises():
  ```
- Avoid testing implementation details; test observable behaviour / public API.

---

## Versioning & tags

- Versioning is dynamic via `hatch-vcs`. Do not hard-code version strings.
- Tag format: `<package-name>:<version>` — e.g. `my-sample-package-provider-core:1.2.3`.
- Non-`devN` tags are only allowed on commits reachable from `main` (enforced by `publish.yml`).
- Pre-release tags (`1.0.0dev1`, `1.0.0.dev2`) are allowed on any branch.

---

## CI

- **CI** (`ci.yml`): runs `ruff check`, `ruff format --check`, and `pytest` on Python 3.11 / 3.12 / 3.13 on every push/PR to `main`.
- **Publish** (`publish.yml`): triggers on `my-sample-package*:*` tags, validates branch policy, builds and publishes via PyPI trusted publishing.
- `uv sync --all-packages` is used in CI — use the same locally before running the full test suite.

---

## Common pitfalls

- **Do not** use `uv run --package X task Y` — it causes infinite recursion. Use `uv run --directory packages/X task Y` instead.
- **Do not** edit `src/<module>/_version.py` — it is auto-generated by `hatch-vcs` and excluded from ruff.
- **Do not** add dev dependencies under `[project.optional-dependencies]`; use `[dependency-groups] dev = [...]` in the root `pyproject.toml`.
- When running `pytest` from the repo root without `--directory`, ensure `uv sync --all-packages` has been run first so all workspace packages are on the path.
