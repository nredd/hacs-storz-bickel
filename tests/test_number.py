"""Tests for the number platform: device-write and option-backed settings."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

from homeassistant.helpers import entity_registry as er

from custom_components.storz_bickel.const import (
    CONF_PUMP_FAILSAFE_SECONDS,
    CONF_TEMP_STEP,
    DEFAULT_PUMP_COOLDOWN_SECONDS,
    DEFAULT_PUMP_FAILSAFE_SECONDS,
    DEFAULT_TEMP_STEP,
    DOMAIN,
)

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from homeassistant.core import HomeAssistant
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    from tests.conftest import FakeDevice

_BLE_LOOKUP = "homeassistant.components.bluetooth.async_ble_device_from_address"
_CREATE_DEVICE = "custom_components.storz_bickel.create_device"


def _entity_id(hass: HomeAssistant, fake_device: FakeDevice, key: str) -> str:
    """Look up a number entity's ID from the registry by unique ID."""
    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id(
        "number", DOMAIN, f"{fake_device.address}_{key}"
    )
    assert entity_id is not None
    return entity_id


async def _set_number(hass: HomeAssistant, entity_id: str, value: float) -> None:
    """Call the number.set_value service."""
    await hass.services.async_call(
        "number",
        "set_value",
        {"entity_id": entity_id, "value": value},
        blocking=True,
    )


async def test_led_brightness_reads_and_writes_device_state(
    hass: HomeAssistant,
    setup_entry: Callable[..., Awaitable[MockConfigEntry]],
    fake_device: FakeDevice,
) -> None:
    """A device-write number reflects device state and calls the device on set."""
    await setup_entry()
    entity_id = _entity_id(hass, fake_device, "led_brightness")

    state = hass.states.get(entity_id)
    assert state is not None
    assert float(state.state) == 70.0

    await _set_number(hass, entity_id, 40)
    assert fake_device.led_brightness_calls == [40]
    state = hass.states.get(entity_id)
    assert state is not None
    assert float(state.state) == 40.0


async def test_option_numbers_default_to_config_defaults(
    hass: HomeAssistant,
    setup_entry: Callable[..., Awaitable[MockConfigEntry]],
    fake_device: FakeDevice,
) -> None:
    """Option-backed numbers read the entry's stored default when unset."""
    await setup_entry()

    failsafe = hass.states.get(_entity_id(hass, fake_device, "pump_failsafe_seconds"))
    assert failsafe is not None
    assert float(failsafe.state) == DEFAULT_PUMP_FAILSAFE_SECONDS

    cooldown = hass.states.get(_entity_id(hass, fake_device, "pump_cooldown_seconds"))
    assert cooldown is not None
    assert float(cooldown.state) == DEFAULT_PUMP_COOLDOWN_SECONDS

    temp_step = hass.states.get(_entity_id(hass, fake_device, "temp_step"))
    assert temp_step is not None
    assert float(temp_step.state) == DEFAULT_TEMP_STEP


async def test_setting_pump_failsafe_number_updates_options_and_reloads(
    hass: HomeAssistant,
    setup_entry: Callable[..., Awaitable[MockConfigEntry]],
    fake_device: FakeDevice,
) -> None:
    """Writing the failsafe number persists to config_entry.options and reloads."""
    entry = await setup_entry()
    entity_id = _entity_id(hass, fake_device, "pump_failsafe_seconds")

    with (
        patch(_BLE_LOOKUP, return_value=MagicMock()),
        patch(_CREATE_DEVICE, return_value=fake_device),
    ):
        await _set_number(hass, entity_id, 90)

    assert entry.options[CONF_PUMP_FAILSAFE_SECONDS] == 90

    state = hass.states.get(_entity_id(hass, fake_device, "pump_failsafe_seconds"))
    assert state is not None
    assert float(state.state) == 90.0


async def test_setting_temp_step_number_updates_options(
    hass: HomeAssistant,
    setup_entry: Callable[..., Awaitable[MockConfigEntry]],
    fake_device: FakeDevice,
) -> None:
    """Writing the temp-step number persists to config_entry.options."""
    entry = await setup_entry()
    entity_id = _entity_id(hass, fake_device, "temp_step")

    with (
        patch(_BLE_LOOKUP, return_value=MagicMock()),
        patch(_CREATE_DEVICE, return_value=fake_device),
    ):
        await _set_number(hass, entity_id, 2.5)

    assert entry.options[CONF_TEMP_STEP] == 2.5


async def test_option_numbers_available_while_disconnected(
    hass: HomeAssistant,
    setup_entry: Callable[..., Awaitable[MockConfigEntry]],
    fake_device: FakeDevice,
) -> None:
    """Option-backed numbers don't depend on a live BLE connection."""
    await setup_entry()

    fake_device.connected = False
    fake_device.fire()
    await hass.async_block_till_done()

    state = hass.states.get(_entity_id(hass, fake_device, "pump_cooldown_seconds"))
    assert state is not None
    assert state.state not in ("unknown", "unavailable")
