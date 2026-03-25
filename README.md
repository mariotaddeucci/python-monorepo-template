# python-monorepo-template

A production-ready template for Python monorepos using [uv workspaces](https://docs.astral.sh/uv/concepts/workspaces/). It provides a structured layout for multiple interdependent packages, a shared toolchain, automated documentation, and a consistent developer experience from day one.

## What's included

- **uv workspace** — all packages share a single lockfile and virtual environment
- **Taskipy** — unified task runner (`test`, `lint`, `autofix`, `format`, `docs`) across all packages with auto-discovery
- **Ruff** — linting and formatting, enforced via pre-commit
- **pytest + pytest-cov** — testing with coverage
- **hatch-vcs** — dynamic versioning from git tags, per package
- **MkDocs Material** — documentation portal with per-package API reference via `mkdocstrings`
- **Pre-commit hooks** — ruff, pyproject-fmt, semgrep, and standard file checks

## Packages

| Package | Module | Min Python | Description |
|---------|--------|-----------|-------------|
| `my-sample-package` | `my_sample_package` | 3.11 | Proxy — re-exports all providers |
| `my-sample-package-provider-core` | `core` | 3.11 | Core utilities and base types |
| `my-sample-package-provider-app` | `app` | 3.12 | Application-level functionality |
| `my-sample-package-provider-standalone` | `standalone` | 3.13 | Standalone, no external deps |

## Quick start

```bash
# Clone
git clone https://github.com/mariotaddeucci/python-monorepo-template.git
cd python-monorepo-template

# Install everything (all packages + dev deps)
uv sync

# Install pre-commit hooks
uv run pre-commit install

# Run all tests
uv run task test

# Lint all packages
uv run task lint

# Serve the documentation portal
uv run task docs
```

## Project structure

```
python-monorepo-template/
├── pyproject.toml          # Workspace root: shared dev deps, ruff, pytest, tasks
├── uv.lock
├── mkdocs.base.yml         # Shared MkDocs Material config
├── mkdocs.yml              # Root documentation portal
├── docs/                   # Portal content
├── scripts/                # Task runner and docs builder
└── packages/
    ├── my-sample-package/
    ├── my-sample-package-provider-core/
    ├── my-sample-package-provider-app/
    └── my-sample-package-provider-standalone/
```

## Contributing

See [CONTRIBUTING](docs/contributing.md) for the full development guide, including setup, code style, testing guidelines, and how to add new packages.

## License

[MIT](LICENSE)
