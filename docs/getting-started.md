# Getting Started

## Prerequisites

- Python >= 3.11
- [uv](https://docs.astral.sh/uv/) package manager

## Installation

```bash
# Clone the repository
git clone https://github.com/mariotaddeucci/python-monorepo-template.git
cd python-monorepo-template

# Install all dependencies (including dev)
uv sync
```

## Running Tasks

All tasks are managed via [taskipy](https://github.com/taskipy/taskipy) and executed through `uv run task`.

### All Packages

```bash
# Run tests across all packages
uv run task test

# Lint all packages
uv run task lint

# Autofix and format all packages
uv run task autofix
uv run task format
```

### Single Package

```bash
# Run tests for a specific package
uv run --directory packages/my-sample-package-provider-core task test

# Lint a specific package
uv run --directory packages/my-sample-package-provider-core task lint
```

## Documentation

```bash
# Serve the portal documentation locally
uv run task docs

# Build all documentation sites
uv run task docs-build

# Serve a specific package's docs
uv run --directory packages/my-sample-package-provider-core task docs
```

## Installing Packages

```bash
# Install the proxy package with all providers
pip install "my-sample-package[all]"

# Or pick individual providers
pip install "my-sample-package[core]"
pip install "my-sample-package[app]"
pip install "my-sample-package[standalone]"
```
