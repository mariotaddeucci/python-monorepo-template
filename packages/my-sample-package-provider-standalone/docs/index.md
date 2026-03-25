# my-sample-package-provider-standalone

Standalone math and text utilities with no external dependencies.

## Installation

```bash
pip install my-sample-package-provider-standalone
```

## Overview

This package provides independent utility functions that have no relationship to the core or app packages.

### Key Components

- **`clamp`** - Clamp a numeric value between a minimum and maximum
- **`lerp`** - Linear interpolation between two values
- **`slugify`** - Convert text to a URL-friendly slug
- **`truncate`** - Truncate text with a configurable suffix

## Quick Start

```python
from standalone import clamp, lerp, slugify, truncate

# Math utilities
value = clamp(15, 0, 10)  # 10
mid = lerp(0, 100, 0.5)   # 50.0

# Text utilities
slug = slugify("Hello World!")  # "hello-world"
short = truncate("A very long text", max_length=10)  # "A very..."
```
