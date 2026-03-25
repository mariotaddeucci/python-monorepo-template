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

This package provides a unified entry point for all providers. It uses a lazy proxy pattern to discover installed providers at import time and re-export their public symbols.

When you import `my_sample_package`, it automatically discovers which provider packages are installed and makes their symbols available directly.
