# Contributing to ts-shape

Thank you for your interest in contributing to ts-shape!

## Ways to Contribute

- Report bugs and issues
- Suggest new features
- Improve documentation
- Submit pull requests with fixes or enhancements
- Add tests for existing functionality

## Development Setup

### 1. Fork and Clone

```bash
git clone https://github.com/your-username/ts-shape.git
cd ts-shape
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Development Dependencies

```bash
pip install -e ".[dev]"
```

### 4. Run Tests

```bash
pytest
pytest --cov=ts_shape  # With coverage
```

## Coding Standards

### Code Style

We use:
- **black** for code formatting
- **flake8** for linting
- **mypy** for type checking

```bash
# Format code
black src/ tests/

# Check linting
flake8 src/ tests/

# Type checking
mypy src/
```

### Design Principles

1. **One UUID Per Signal** - Keep it simple
2. **DataFrame In, DataFrame Out** - Consistent interface
3. **No Over-Engineering** - Solve the actual problem
4. **Practical Daily Questions** - Focus on real plant manager needs
5. **Comprehensive Tests** - All new code must have tests

### Documentation

- Add docstrings to all public methods
- Follow Google docstring format
- Include usage examples
- Update relevant .md files

Example:
```python
def method_name(self, param1: str, *, param2: int = 10) -> pd.DataFrame:
    """Brief description of what method does.

    Args:
        param1: Description of param1
        param2: Description of param2 (default: 10)

    Returns:
        DataFrame with columns:
        - column1: Description
        - column2: Description

    Example:
        >>> tracker = ModuleName(df)
        >>> result = tracker.method_name('value')
            column1  column2
        0   data     data
    """
```

## Pull Request Process

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Write code following style guidelines
- Add tests for new functionality
- Update documentation

### 3. Run Tests and Checks

```bash
# Run tests
pytest

# Format code
black src/ tests/

# Check linting
flake8 src/ tests/

# Verify all tests pass
pytest --cov=ts_shape
```

### 4. Commit Changes

Use clear, descriptive commit messages:

```bash
git add .
git commit -m "feat: add OEE tracking module

- Implement OEETracking class
- Add oee_by_shift() method
- Add comprehensive tests
- Update documentation"
```

Commit message format:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation
- `test:` for tests
- `refactor:` for refactoring
- `perf:` for performance improvements

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear description of changes
- Reference to related issues
- Test results
- Screenshots (if UI changes)

## Testing Guidelines

### Test Structure

```python
import pytest
import pandas as pd
from ts_shape.events.production import ModuleName

@pytest.fixture
def sample_data():
    """Create sample test data."""
    return pd.DataFrame({...})

def test_method_basic(sample_data):
    """Test basic functionality."""
    tracker = ModuleName(sample_data)
    result = tracker.method()

    assert not result.empty
    assert 'expected_column' in result.columns

def test_method_edge_case():
    """Test edge cases."""
    df_empty = pd.DataFrame(columns=['uuid', 'systime'])
    tracker = ModuleName(df_empty)
    result = tracker.method()

    assert result.empty
```

### Test Coverage

- Aim for >90% code coverage
- Test all public methods
- Test edge cases (empty data, single values, etc.)
- Test error handling

## Documentation Guidelines

### User Guide Updates

When adding new features, update:
- Quick start guide if applicable
- Module-specific documentation
- API reference (auto-generated)
- Add examples to relevant sections

### Example Format

```markdown
### New Feature Name

**What**: Brief description

**Why Needed**: Business justification

**Example**:
\`\`\`python
from ts_shape.events.production import NewModule

tracker = NewModule(df)
result = tracker.new_method(param='value')
\`\`\`

**Returns**:
- column1: Description
- column2: Description
```

## Release Process

Maintainers will:
1. Review and merge PRs
2. Update CHANGELOG.md
3. Bump version number
4. Create GitHub release
5. Publish to PyPI
6. Deploy documentation

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Focus on what's best for the community
- Show empathy towards others
- Accept constructive criticism gracefully
- Help others learn and grow

### Unacceptable Behavior

- Harassment or discriminatory language
- Trolling or insulting comments
- Personal or political attacks
- Publishing others' private information

## Questions?

- Check existing [issues](https://github.com/your-org/ts-shape/issues)
- Join discussions
- Ask for help in PRs

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to ts-shape! 🎉
