# my-sample-package-provider-core

Core models and utility functions.

## Installation

```bash
pip install my-sample-package-provider-core
```

## Overview

This package provides the foundational data models and utility functions used across the monorepo.

### Key Components

- **`DataModel`** - Core data model with serialization support (`to_dict`, `from_dict`)
- **`format_message`** - Template-based message formatting
- **`process_data`** - Data processing utility that converts raw records to `DataModel` instances
- **`filter_by_tag`** - Tag-based filtering for `DataModel` collections

## Quick Start

```python
from core import DataModel, format_message, process_data

# Create a model
model = DataModel(id=1, name="example", value=42.0, tags=["demo"])

# Serialize
data = model.to_dict()

# Format a message
msg = format_message("Hello, {name}!", name="World")
```
