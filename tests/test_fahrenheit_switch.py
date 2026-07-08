"""Tests for the device-side Fahrenheit-display switch."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers import entity_registry as er

from custom_components.storz_bickel.api import DeviceType, capabilities_for
from custom_components.storz_bickel.const import DOMAIN

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from homeassistant.core import HomeAssistant
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    from tests.conftest import FakeDevice


def _fahrenheit_entity_id(hass: HomeAssistant, fake_device: FakeDevice) -> str | None:
    """Look up the Fahrenheit-display switch's entity ID from the registry."""
    registry = er.async_get(hass)
    return registry.async_get_entity_id(
        "switch", DOMAIN, f"{fake_device.address}_fahrenheit_display"
    )


async def test_fahrenheit_switch_present_and_calls_device(
    hass: HomeAssistant,
    setup_entry: Callable[..., Awaitable[MockConfigEntry]],
    fake_device: FakeDevice,
) -> None:
    """The switch is present for the Volcano and forwards turn_on to the device."""
    await setup_entry()
    entity_id = _fahrenheit_entity_id(hass, fake_device)
    assert entity_id is not None

    await hass.services.async_call(
        "switch", "turn_on", {"entity_id": entity_id}, blocking=True
    )
    assert fake_device.fahrenheit_calls == [True]

    await hass.services.async_call(
        "switch", "turn_off", {"entity_id": entity_id}, blocking=True
    )
    assert fake_device.fahrenheit_calls == [True, False]


async def test_fahrenheit_switch_absent_without_capability(
    hass: HomeAssistant,
    setup_entry: Callable[..., Awaitable[MockConfigEntry]],
    fake_device: FakeDevice,
) -> None:
    """The switch is not created for devices without the capability (e.g. Crafty)."""
    fake_device.capabilities = capabilities_for(DeviceType.CRAFTY)
    await setup_entry()
    assert _fahrenheit_entity_id(hass, fake_device) is None
