"""Sample test module demonstrating pytest marker usage."""

import pytest


@pytest.mark.unit
def test_example_unit():
    """Example unit test."""
    assert True


@pytest.mark.integration
def test_example_integration():
    """Example integration test."""
    assert True


@pytest.mark.requires_app
def test_example_requires_app():
    """Example test that requires the application."""
    assert True


@pytest.mark.slow
def test_example_slow():
    """Example slow running test."""
    assert True


@pytest.mark.slack
def test_example_slack():
    """Example test related to slack functionality."""
    assert True


@pytest.mark.asl
def test_example_asl():
    """Example test related to ASL functionality."""
    assert True


# Demonstrate filterwarnings decorator usage
@pytest.mark.filterwarnings("ignore:specific warning message")
def test_with_specific_warning_filter():
    """Example test with specific warning filter."""
    assert True


# Multiple markers can be combined
@pytest.mark.unit
@pytest.mark.asl
def test_combined_markers():
    """Example test with multiple markers."""
    assert True
