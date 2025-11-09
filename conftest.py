"""Pytest configuration file for ASL Monitoring System."""

import pytest


def pytest_configure(config):
    """Register custom markers to avoid warnings."""
    custom_markers = [
        "unit",
        "integration",
        "requires_app",
        "slow",
        "slack",
        "asl"
    ]
    for marker in custom_markers:
        config.addinivalue_line(
            "markers", f"{marker}: mark test as {marker}"
        )
