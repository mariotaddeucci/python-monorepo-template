# Usage

## Basic Usage

```python
import my_sample_package as msp

# Symbols from installed providers are available directly
model = msp.DataModel(id=1, name="example")
result = msp.clamp(5, 0, 10)
```

## Selecting Providers

Install only the providers you need:

=== "All providers"

    ```bash
    pip install "my-sample-package[all]"
    ```

=== "Core only"

    ```bash
    pip install "my-sample-package[core]"
    ```

=== "App only"

    ```bash
    pip install "my-sample-package[app]"
    ```

=== "Standalone only"

    ```bash
    pip install "my-sample-package[standalone]"
    ```

## Available Symbols

The available symbols depend on which providers are installed:

| Provider | Symbols |
|----------|---------|
| `core` | `DataModel`, `format_message`, `process_data` |
| `app` | `Pipeline`, `Reporter` |
| `standalone` | `clamp`, `lerp`, `slugify`, `truncate` |

## API Reference

::: my_sample_package
    options:
      show_source: true
      show_root_heading: true
