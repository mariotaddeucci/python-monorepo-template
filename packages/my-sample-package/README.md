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

## Usage

```python
import my_sample_package as msp

# Symbols from installed providers are available directly
model = msp.DataModel(id=1, name="example")
result = msp.clamp(5, 0, 10)
```
