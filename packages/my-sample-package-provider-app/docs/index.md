# my-sample-package-provider-app

Pipeline and reporting functionality.

## Installation

```bash
pip install my-sample-package-provider-app
```

## Overview

This package provides application-level components for data processing and reporting.

### Key Components

- **`Pipeline`** - Data loading and filtering pipeline with method chaining support
- **`Reporter`** - Summary generation and serialization for processed data

### Optional Core Integration

If `my-sample-package-provider-core` is installed, the `Pipeline` class automatically converts raw dictionaries into `DataModel` instances for richer functionality.

```bash
# Install with core integration
pip install "my-sample-package-provider-app[core]"
```

## Quick Start

```python
from app import Pipeline, Reporter

# Create a pipeline
pipeline = Pipeline()
pipeline.load([{"id": 1, "name": "test", "value": 10.0}])

# Generate a report
reporter = Reporter(pipeline.results())
print(reporter.summary())
```
