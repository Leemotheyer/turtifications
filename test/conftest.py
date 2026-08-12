"""Shared pytest setup for local and CI runs."""

import pytest

from functions.config import initialize_files


@pytest.fixture(scope="session", autouse=True)
def ensure_data_files_exist():
    """Create default config/log files so tests can run in clean environments."""
    initialize_files()
