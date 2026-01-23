# Installation

## Requirements

- Python 3.8 or higher
- pandas >= 1.3.0
- numpy >= 1.20.0

## Install from PyPI

```bash
pip install ts-shape
```

## Install from Source

```bash
git clone https://github.com/your-org/ts-shape.git
cd ts-shape
pip install -e .
```

## Verify Installation

```python
import ts_shape
from ts_shape.events.production import PartProductionTracking

print("ts-shape installed successfully!")
```

## Optional Dependencies

For enhanced functionality:

```bash
# For advanced analytics
pip install scikit-learn

# For visualization
pip install matplotlib seaborn

# For Jupyter notebook support
pip install jupyter ipywidgets
```

## Development Installation

If you want to contribute:

```bash
git clone https://github.com/your-org/ts-shape.git
cd ts-shape

# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
black src/
flake8 src/
```

## Docker Installation

```bash
docker pull your-org/ts-shape:latest
docker run -it your-org/ts-shape:latest python
```

## Troubleshooting

### Common Issues

**Issue**: ImportError for ts_shape
```bash
# Solution: Make sure you're in the right environment
which python
pip list | grep ts-shape
```

**Issue**: pandas version conflict
```bash
# Solution: Upgrade pandas
pip install --upgrade pandas
```

**Issue**: Performance issues with large datasets
```bash
# Solution: Install optional performance packages
pip install numba pyarrow
```

## Next Steps

- [Quick Start Guide](quick_start.md)
- [Daily Production Modules](daily_production.md)
- [Complete User Guide](complete_guide.md)
