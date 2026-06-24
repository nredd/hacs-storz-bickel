"""Shared pytest fixtures for the Storz & Bickel integration tests."""

from __future__ import annotations

from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable loading of the custom integration in every test."""
    return


@pytest.fixture
def expected_lingering_timers() -> bool:
    """Tolerate the bluetooth manager's periodic availability-check timer.

    Setting up the ``bluetooth`` dependency schedules a recurring timer that the
    bundled test mocks do not fully tear down; Home Assistant core's own
    bluetooth tests tolerate it the same way.
    """
    return True


@pytest.fixture(autouse=True)
def _mock_linux_bt_history():
    """Stub the Linux adapter history (the bundled bluetooth mock leaves it un-stubbed).

    Without this, setting up the ``bluetooth`` dependency in tests hits the real
    BlueZ/DBus code path and fails on CI and dev machines.
    """
    with patch("bluetooth_adapters.systems.linux.LinuxAdapters.history", {}):
        yield
