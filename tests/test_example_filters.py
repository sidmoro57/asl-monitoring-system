"""Sample test module demonstrating module-level warning filters."""

import pytest

# Module-level filter - applies to all tests in this file
pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")


@pytest.mark.unit
def test_with_module_filter():
    """Example test with module-level warning filter."""
    # This test will ignore DeprecationWarnings due to pytestmark
    assert True


@pytest.mark.asl
def test_another_with_module_filter():
    """Another test benefiting from module-level filter."""
    assert True
