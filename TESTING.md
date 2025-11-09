# Testing Guide for ASL Monitoring System

This project uses pytest for testing with custom markers and warning filters configured.

## Running Tests

### Run all tests
```bash
pytest
```

### Run with verbose output
```bash
pytest -v
```

### Run specific test file
```bash
pytest tests/test_isengard.py
```

### Disable warnings entirely for specific runs
```bash
pytest --disable-warnings
```

## Custom Markers

The following custom markers are registered and available for use:

- **`@pytest.mark.unit`** - Mark test as a unit test
- **`@pytest.mark.integration`** - Mark test as an integration test
- **`@pytest.mark.requires_app`** - Mark test that requires the application
- **`@pytest.mark.slow`** - Mark test as slow running
- **`@pytest.mark.slack`** - Mark test related to slack functionality
- **`@pytest.mark.asl`** - Mark test related to ASL functionality

### Using Markers

```python
import pytest

@pytest.mark.unit
def test_something():
    assert True

# Multiple markers can be combined
@pytest.mark.unit
@pytest.mark.asl
def test_combined():
    assert True
```

### Filtering Tests by Markers

```bash
# Run only unit tests
pytest -m "unit"

# Run integration tests
pytest -m "integration"

# Run slow or slack tests
pytest -m "slow or slack"

# Run unit tests but not slow ones
pytest -m "unit and not slow"
```

## Warning Filters

### Global Configuration

The project is configured to:
- Convert all warnings to errors (helps catch issues early)
- Ignore `UserWarning` messages
- Ignore `DeprecationWarning` messages

These settings are in `pytest.ini`.

### Test-Specific Warning Filters

For specific tests that need custom warning handling:

```python
@pytest.mark.filterwarnings("ignore:specific warning message")
def test_something():
    # This test will ignore the specific warning
    pass
```

### Module-Level Warning Filters

To apply warning filters to all tests in a file:

```python
import pytest

# At the top of your test file
pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")

def test_something():
    # This test benefits from the module-level filter
    pass
```

## Project Structure

```
asl-monitoring-system/
├── pytest.ini          # Pytest configuration with markers and filters
├── conftest.py         # Pytest hooks and shared fixtures
└── tests/              # Test directory
    ├── __init__.py
    ├── test_isengard.py
    └── test_example_filters.py
```

## Configuration Files

### pytest.ini

Contains:
- Marker definitions
- Global warning filters
- Other pytest configuration options

### conftest.py

Contains:
- Dynamic marker registration via `pytest_configure` hook
- Shared fixtures (when added)
- Test setup/teardown logic (when needed)

## Best Practices

1. **Use appropriate markers**: Tag tests with relevant markers to enable selective test runs
2. **Handle warnings properly**: Register markers to avoid pytest warnings about unknown markers
3. **Keep tests isolated**: Each test should be independent and not rely on others
4. **Use descriptive names**: Test function names should clearly describe what they test
5. **Document complex tests**: Add docstrings to explain non-obvious test logic

## Examples

See the following test files for examples:
- `tests/test_isengard.py` - Examples of all marker types and warning filters
- `tests/test_example_filters.py` - Module-level warning filter example

## Troubleshooting

### "Unknown marker" warnings

If you see warnings about unknown markers, ensure:
1. The marker is registered in `pytest.ini`
2. The marker is registered in `conftest.py`'s `pytest_configure` function

### Warning-related failures

If tests fail due to warnings:
1. Check if the warning should be fixed or ignored
2. Add appropriate filterwarnings in pytest.ini or test decorators
3. Use `pytest --disable-warnings` for debugging (not recommended for regular runs)

### Tests not found

Ensure:
1. Test files are named `test_*.py` or `*_test.py`
2. Test functions are named `test_*`
3. The `tests/` directory has an `__init__.py` file
