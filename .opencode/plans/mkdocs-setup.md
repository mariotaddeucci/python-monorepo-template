# MkDocs Material - Monorepo Documentation Plan

## Approach: Independent Sites with Central Portal

Each package has its own `mkdocs.yml` and `docs/`, buildable independently.
A root site serves as a hub/portal linking to each package's documentation.
Shared config via MkDocs `INHERIT` from a `mkdocs.base.yml`.
API docs auto-generated via `mkdocstrings[python]`.

---

## Files to Create

### 1. `mkdocs.base.yml` (shared config)

```yaml
theme:
  name: material
  palette:
    - scheme: default
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - scheme: slate
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.expand
    - navigation.top
    - content.code.copy
    - content.code.annotate
    - search.highlight
    - search.suggest

markdown_extensions:
  admonition: {}
  pymdownx.details: {}
  pymdownx.superfences: {}
  pymdownx.highlight:
    anchor_linenums: true
  pymdownx.inlinehilite: {}
  pymdownx.tabbed:
    alternate_style: true
  toc:
    permalink: true
  attr_list: {}
  md_in_html: {}
  pymdownx.emoji:
    emoji_index: !!python/name:material.extensions.emoji.twemoji
    emoji_generator: !!python/name:material.extensions.emoji.to_svg
```

### 2. `mkdocs.yml` (root portal)

```yaml
INHERIT: mkdocs.base.yml

site_name: Python Monorepo Template
site_description: Documentation for the Python Monorepo Template
repo_url: https://github.com/mariotaddeucci/python-monorepo-template
repo_name: python-monorepo-template

docs_dir: docs/
site_dir: site/

nav:
  - Home: index.md
  - Getting Started: getting-started.md
  - Architecture: architecture.md
  - Contributing: contributing.md

plugins:
  - search
```

### 3. `docs/index.md` (portal landing page)

```markdown
# Python Monorepo Template

Welcome to the Python Monorepo Template documentation.

## Packages

<div class="grid cards" markdown>

- :material-package-variant: **my-sample-package**

    ---

    Proxy package that re-exports all symbols from installed providers.

    [:octicons-arrow-right-24: Documentation](packages/my-sample-package/)

- :material-cube-outline: **provider-core**

    ---

    Core models and utilities.

    [:octicons-arrow-right-24: Documentation](packages/my-sample-package-provider-core/)

- :material-application-outline: **provider-app**

    ---

    Pipeline and reporting functionality.

    [:octicons-arrow-right-24: Documentation](packages/my-sample-package-provider-app/)

- :material-rocket-launch-outline: **provider-standalone**

    ---

    Standalone math and text utilities.

    [:octicons-arrow-right-24: Documentation](packages/my-sample-package-provider-standalone/)

</div>
```

### 4. `docs/getting-started.md`

```markdown
# Getting Started

<!-- TODO: Add getting started content -->

## Prerequisites

- Python >= 3.11
- [uv](https://docs.astral.sh/uv/) package manager

## Installation

```bash
# Clone the repository
git clone https://github.com/mariotaddeucci/python-monorepo-template.git
cd python-monorepo-template

# Install dependencies
uv sync
```

## Quick Start

```bash
# Run tests
uv run task test

# Lint
uv run task lint

# Format
uv run task format
```

```

### 5. `docs/architecture.md`

```markdown
# Architecture

<!-- TODO: Add architecture overview -->

## Monorepo Structure

This project follows a monorepo pattern using [uv workspaces](https://docs.astral.sh/uv/concepts/workspaces/).

```

python-monorepo-template/
├── pyproject.toml          # workspace root
├── uv.lock
└── packages/
    ├── my-sample-package/                     # proxy package
    ├── my-sample-package-provider-core/       # core provider (Python >=3.11)
    ├── my-sample-package-provider-app/        # app provider (Python >=3.12)
    └── my-sample-package-provider-standalone/ # standalone provider (Python >=3.13)

```

## Package Relationships

<!-- TODO: Add package dependency diagram -->

## Versioning

Versions are managed dynamically via `hatch-vcs`. Tag format: `<package-name>:<version>`.
```

### 6. `docs/contributing.md`

```markdown
# Contributing

<!-- TODO: Add contributing guidelines -->

## Development Setup

```bash
uv sync
```

## Code Style

- Line length: 120 chars
- Indentation: 4 spaces
- Quotes: double (`"`)
- Full type annotations on all public functions
- Google-style docstrings

## Running Tests

```bash
# All packages
uv run task test

# Single package
uv run --directory packages/my-sample-package-provider-core task test
```

## Linting

```bash
uv run task lint
uv run task autofix
uv run task format
```

```

### 7. `packages/my-sample-package/mkdocs.yml`

```yaml
INHERIT: ../../mkdocs.base.yml

site_name: my-sample-package

docs_dir: docs/
site_dir: ../../site/packages/my-sample-package/

nav:
  - Overview: index.md
  - Usage: usage.md

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          paths: [src]
          options:
            show_source: true
            show_root_heading: true
```

### 8. `packages/my-sample-package/docs/index.md`

```markdown
# my-sample-package

Proxy package that re-exports all symbols from installed `my-sample-package-provider-*` packages.

## Installation

```bash
# Install with all providers
pip install "my-sample-package[all]"

# Or pick individual providers
pip install "my-sample-package[core]"
pip install "my-sample-package[app]"
pip install "my-sample-package[standalone]"
```

## Overview

<!-- TODO: Add package overview -->
```

### 9. `packages/my-sample-package/docs/usage.md`

```markdown
# Usage

<!-- TODO: Add usage examples -->

```python
import my_sample_package as msp

# Symbols from installed providers are available directly
model = msp.DataModel(id=1, name="example")
result = msp.clamp(5, 0, 10)
```

```

### 10. `packages/my-sample-package-provider-core/mkdocs.yml`

```yaml
INHERIT: ../../mkdocs.base.yml

site_name: my-sample-package-provider-core

docs_dir: docs/
site_dir: ../../site/packages/my-sample-package-provider-core/

nav:
  - Overview: index.md
  - API Reference: api/reference.md

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          paths: [src]
          options:
            show_source: true
            show_root_heading: true
            members_order: source
```

### 11. `packages/my-sample-package-provider-core/docs/index.md`

```markdown
# my-sample-package-provider-core

Core models and utility functions.

## Installation

```bash
pip install my-sample-package-provider-core
```

## Overview

<!-- TODO: Add package overview -->

This package provides:

- `DataModel` - Core data model with serialization support
- `format_message` - Template-based message formatting
- `process_data` - Data processing utilities
- `filter_by_tag` - Tag-based filtering

```

### 12. `packages/my-sample-package-provider-core/docs/api/reference.md`

```markdown
# API Reference

## Models

::: core.models
    options:
      show_source: true

## Utils

::: core.utils
    options:
      show_source: true
```

### 13. `packages/my-sample-package-provider-app/mkdocs.yml`

```yaml
INHERIT: ../../mkdocs.base.yml

site_name: my-sample-package-provider-app

docs_dir: docs/
site_dir: ../../site/packages/my-sample-package-provider-app/

nav:
  - Overview: index.md
  - API Reference: api/reference.md

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          paths: [src]
          options:
            show_source: true
            show_root_heading: true
            members_order: source
```

### 14. `packages/my-sample-package-provider-app/docs/index.md`

```markdown
# my-sample-package-provider-app

Pipeline and reporting functionality.

## Installation

```bash
pip install my-sample-package-provider-app
```

## Overview

<!-- TODO: Add package overview -->

This package provides:

- `Pipeline` - Data loading and filtering pipeline
- `Reporter` - Summary and serialization reporting

```

### 15. `packages/my-sample-package-provider-app/docs/api/reference.md`

```markdown
# API Reference

## Pipeline

::: app.pipeline
    options:
      show_source: true

## Reporter

::: app.reporter
    options:
      show_source: true
```

### 16. `packages/my-sample-package-provider-standalone/mkdocs.yml`

```yaml
INHERIT: ../../mkdocs.base.yml

site_name: my-sample-package-provider-standalone

docs_dir: docs/
site_dir: ../../site/packages/my-sample-package-provider-standalone/

nav:
  - Overview: index.md
  - API Reference: api/reference.md

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          paths: [src]
          options:
            show_source: true
            show_root_heading: true
            members_order: source
```

### 17. `packages/my-sample-package-provider-standalone/docs/index.md`

```markdown
# my-sample-package-provider-standalone

Standalone math and text utilities.

## Installation

```bash
pip install my-sample-package-provider-standalone
```

## Overview

<!-- TODO: Add package overview -->

This package provides:

- `clamp` - Clamp a value between min and max
- `lerp` - Linear interpolation
- `slugify` - Convert text to URL-friendly slug
- `truncate` - Truncate text with suffix

```

### 18. `packages/my-sample-package-provider-standalone/docs/api/reference.md`

```markdown
# API Reference

## Math

::: standalone.math
    options:
      show_source: true

## Text

::: standalone.text
    options:
      show_source: true
```

### 19. `scripts/build_docs.py`

```python
"""Build or serve documentation for the monorepo.

Usage:
    uv run python scripts/build_docs.py build    # Build all docs
    uv run python scripts/build_docs.py serve    # Serve root docs only
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKAGES_DIR = ROOT / "packages"
SITE_DIR = ROOT / "site"


def find_packages() -> list[Path]:
    """Find all packages that have a mkdocs.yml file."""
    return sorted(p.parent for p in PACKAGES_DIR.glob("*/mkdocs.yml"))


def build_root() -> None:
    """Build the root documentation site."""
    print("Building root documentation...")
    subprocess.run(
        ["uv", "run", "mkdocs", "build", "--config-file", str(ROOT / "mkdocs.yml")],
        cwd=str(ROOT),
        check=True,
    )


def build_package(package_dir: Path) -> None:
    """Build documentation for a single package."""
    config_file = package_dir / "mkdocs.yml"
    print(f"Building docs for {package_dir.name}...")
    subprocess.run(
        ["uv", "run", "mkdocs", "build", "--config-file", str(config_file)],
        cwd=str(package_dir),
        check=True,
    )


def build_all() -> None:
    """Build all documentation sites."""
    build_root()
    for package_dir in find_packages():
        build_package(package_dir)
    print(f"\nAll docs built successfully in {SITE_DIR}/")


def serve() -> None:
    """Serve the root documentation site."""
    print("Serving root documentation...")
    print("Note: To serve a specific package, run:")
    print("  uv run --directory packages/<name> mkdocs serve")
    subprocess.run(
        ["uv", "run", "mkdocs", "serve", "--config-file", str(ROOT / "mkdocs.yml")],
        cwd=str(ROOT),
        check=True,
    )


def main() -> None:
    """Entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/build_docs.py [build|serve]")
        sys.exit(1)

    command = sys.argv[1]
    if command == "build":
        build_all()
    elif command == "serve":
        serve()
    else:
        print(f"Unknown command: {command}")
        print("Usage: python scripts/build_docs.py [build|serve]")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

---

## Files to Edit

### 20. `pyproject.toml` (root) - Add deps and tasks

Add to `[dependency-groups] dev`:

```
"mkdocs>=1.6",
"mkdocs-material>=9.5",
"mkdocstrings[python]>=0.25",
```

Add/update taskipy tasks:

```toml
docs       = { cmd = "uv run python scripts/build_docs.py serve", help = "Serve documentation" }
docs-build = { cmd = "uv run python scripts/build_docs.py build", help = "Build all documentation" }
```

### 21. `.gitignore` - Add site/

Add:

```
site/
```

### 22. Each `packages/*/pyproject.toml` - Add docs task

Add to each package's `[tool.taskipy.tasks]`:

```toml
docs = { cmd = "uv run mkdocs serve", help = "Serve package docs" }
```

---

## Directory Structure Summary

```
python-monorepo-template/
├── mkdocs.base.yml                    # NEW: shared config
├── mkdocs.yml                         # NEW: portal site
├── docs/                              # NEW: portal docs
│   ├── index.md
│   ├── getting-started.md
│   ├── architecture.md
│   └── contributing.md
├── scripts/
│   ├── run_task.py                    # existing
│   └── build_docs.py                 # NEW: docs build script
└── packages/
    ├── my-sample-package/
    │   ├── mkdocs.yml                # NEW
    │   └── docs/                     # NEW
    │       ├── index.md
    │       └── usage.md
    ├── my-sample-package-provider-core/
    │   ├── mkdocs.yml                # NEW
    │   └── docs/                     # NEW
    │       ├── index.md
    │       └── api/
    │           └── reference.md
    ├── my-sample-package-provider-app/
    │   ├── mkdocs.yml                # NEW
    │   └── docs/                     # NEW
    │       ├── index.md
    │       └── api/
    │           └── reference.md
    └── my-sample-package-provider-standalone/
        ├── mkdocs.yml                # NEW
        └── docs/                     # NEW
            ├── index.md
            └── api/
                └── reference.md
```

## Key Design Decisions

1. **INHERIT pattern**: All package mkdocs.yml files inherit from `../../mkdocs.base.yml`, ensuring consistent theming and extensions across all sites.
2. **site_dir convention**: Each package outputs to `../../site/packages/<name>/`, placing all built sites under the root `site/` directory.
3. **mkdocstrings**: Each package's mkdocs.yml configures `paths: [src]` so the Python handler can resolve modules from the package's source code.
4. **Independent serving**: Each package can be served standalone with `uv run --directory packages/<name> mkdocs serve` for isolated development.
5. **Portal with grid cards**: The root `docs/index.md` uses Material's grid cards to create a visual directory of all packages with links.
