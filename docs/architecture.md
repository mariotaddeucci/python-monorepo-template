# Architecture

## Monorepo Structure

This project follows a monorepo pattern using [uv workspaces](https://docs.astral.sh/uv/concepts/workspaces/).

```
python-monorepo-template/
├── pyproject.toml          # workspace root: ruff, pytest, taskipy
├── uv.lock
└── packages/
    ├── my-sample-package/                     # proxy package — re-exports all providers
    ├── my-sample-package-provider-core/       # Python >=3.11, module: core
    ├── my-sample-package-provider-app/        # Python >=3.12, module: app
    └── my-sample-package-provider-standalone/ # Python >=3.13, module: standalone
```

Each package contains: `src/<module>/`, `tests/`, `pyproject.toml`, `.python-version`, `README.md`.

## Package Relationships

<!-- TODO: Add package dependency diagram -->

| Package | Module | Python | Description |
|---------|--------|--------|-------------|
| `my-sample-package` | `my_sample_package` | >= 3.11 | Proxy that re-exports all provider symbols |
| `my-sample-package-provider-core` | `core` | >= 3.11 | Core data models and utilities |
| `my-sample-package-provider-app` | `app` | >= 3.12 | Pipeline and reporting (optionally depends on core) |
| `my-sample-package-provider-standalone` | `standalone` | >= 3.13 | Independent math and text utilities |

## Proxy Pattern

The `my-sample-package` package uses a lazy proxy pattern.
It discovers installed providers at import time and dynamically
re-exports their public symbols via `__getattr__`.

## Versioning

Versions are managed dynamically via `hatch-vcs`. Each package is versioned independently using git tags.

Tag format: `<package-name>:<version>` (e.g., `my-sample-package-provider-core:1.2.3`).

## Toolchain

| Tool | Purpose |
|------|---------|
| [uv](https://docs.astral.sh/uv/) | Package manager and workspace orchestration |
| [ruff](https://docs.astral.sh/ruff/) | Linting and formatting |
| [pytest](https://docs.pytest.org/) | Testing |
| [taskipy](https://github.com/taskipy/taskipy) | Task runner |
| [hatch-vcs](https://github.com/ofek/hatch-vcs) | Dynamic versioning from git tags |
| [mkdocs-material](https://squidfunk.github.io/mkdocs-material/) | Documentation |
