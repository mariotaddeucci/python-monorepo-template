# Python Monorepo Template

Welcome to the Python Monorepo Template documentation.

This monorepo uses [uv workspaces](https://docs.astral.sh/uv/concepts/workspaces/)
to manage multiple Python packages in a single repository.

## Packages

<div class="grid cards" markdown>

- :material-package-variant: **my-sample-package**

    ---

    Proxy package that re-exports all symbols from installed providers.

    [:octicons-arrow-right-24: Documentation](packages/my-sample-package/)

- :material-cube-outline: **provider-core**

    ---

    Core models and utilities. Python >= 3.11.

    [:octicons-arrow-right-24: Documentation](packages/my-sample-package-provider-core/)

- :material-application-outline: **provider-app**

    ---

    Pipeline and reporting functionality. Python >= 3.12.

    [:octicons-arrow-right-24: Documentation](packages/my-sample-package-provider-app/)

- :material-rocket-launch-outline: **provider-standalone**

    ---

    Standalone math and text utilities. Python >= 3.13.

    [:octicons-arrow-right-24: Documentation](packages/my-sample-package-provider-standalone/)

</div>

## Quick Start

```bash
# Clone the repository
git clone https://github.com/mariotaddeucci/python-monorepo-template.git
cd python-monorepo-template

# Install dependencies
uv sync

# Run tests
uv run task test

# Serve documentation
uv run task docs
```
