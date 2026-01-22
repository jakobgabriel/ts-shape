# ts-shape Documentation

This directory contains the source files for ts-shape documentation.

## Building the Documentation Locally

### Prerequisites

```bash
pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints myst-parser
pip install -e ..  # Install ts-shape in development mode
```

### Build HTML Documentation

```bash
cd docs
make html
```

The generated HTML will be in `_build/html/`. Open `_build/html/index.html` in your browser.

### Build PDF Documentation

```bash
make latexpdf
```

### Clean Build Files

```bash
make clean
```

## Documentation Structure

```
docs/
├── index.rst              # Main documentation index
├── conf.py                # Sphinx configuration
├── Makefile               # Build commands
├── user_guide/            # User guides and tutorials
│   ├── installation.md
│   ├── quick_start.md
│   ├── daily_production.md → ../../DAILY_PRODUCTION_MODULES.md
│   ├── downtime_quality.md → ../../DOWNTIME_QUALITY_MODULES.md
│   └── complete_guide.md → ../../PRODUCTION_MODULES_SUMMARY.md
├── modules/               # Module documentation
│   └── production/
│       └── index.rst
├── api/                   # API reference (auto-generated)
│   └── production.rst
├── resources/             # Additional resources
│   ├── future_features.md → ../../FUTURE_PRODUCTION_FEATURES.md
│   ├── contributing.md
│   └── changelog.md
├── _static/               # Static files (images, CSS)
└── _templates/            # Custom templates
```

## Automatic Deployment

Documentation is automatically built and deployed to GitHub Pages when:
- Code is pushed to `main` or `master` branch
- A pull request is merged
- Manually triggered via GitHub Actions

The workflow is defined in `.github/workflows/deploy-docs.yml`.

## Writing Documentation

### Markdown Files

Use MyST Markdown for documentation:

```markdown
# Section Title

## Subsection

**Bold text**, *italic text*

- Bullet point
- Another point

\`\`\`python
# Code example
from ts_shape.production import PartProductionTracking
tracker = PartProductionTracking(df)
\`\`\`
```

### reStructuredText Files

For more complex documentation:

```rst
Section Title
=============

.. code-block:: python

   from ts_shape.production import PartProductionTracking
   tracker = PartProductionTracking(df)

.. note::
   This is a note.

.. warning::
   This is a warning.
```

### API Documentation

API documentation is auto-generated from docstrings:

```python
def method_name(self, param: str) -> pd.DataFrame:
    """Brief description.

    Args:
        param: Description of parameter

    Returns:
        DataFrame with columns:
        - col1: Description
        - col2: Description

    Example:
        >>> tracker = Module(df)
        >>> result = tracker.method_name('value')
    """
```

## Previewing Changes

After making changes:

1. Build the docs: `make html`
2. Open `_build/html/index.html` in a browser
3. Check formatting, links, and examples

## Common Issues

### Module Import Errors

Make sure ts-shape is installed:
```bash
cd ..
pip install -e .
```

### Missing Extensions

Install required Sphinx extensions:
```bash
pip install sphinx-rtd-theme sphinx-autodoc-typehints myst-parser
```

### Broken Links

Check for broken links:
```bash
make linkcheck
```

## Contributing

See [Contributing Guide](resources/contributing.md) for details on:
- Documentation standards
- Code examples format
- Review process

## Questions?

- Check [existing documentation](https://your-org.github.io/ts-shape)
- Open an issue on GitHub
- Review [contributing guide](resources/contributing.md)
