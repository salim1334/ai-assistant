"""Pytest fixtures for legacy and customer-ready tests."""

import pytest

from enhanced_bdfg.tests.test_framework import create_test_data


@pytest.fixture
def test_data():
    return create_test_data()
