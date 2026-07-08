"""Options flow tests for the Storz & Bickel integration."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_ADDRESS, UnitOfTemperature
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.storz_bickel.const import (
    CONF_DEVICE_TYPE,
    CONF_PUMP_COOLDOWN_ENABLED,
    CONF_PUMP_COOLDOWN_SECONDS,
    CONF_PUMP_FAILSAFE_ENABLED,
    CONF_PUMP_FAILSAFE_SECONDS,
    CONF_TEMPERATURE_UNIT,
    DEFAULT_PUMP_COOLDOWN_ENABLED,
    DEFAULT_PUMP_COOLDOWN_SECONDS,
    DEFAULT_PUMP_FAILSAFE_ENABLED,
    DEFAULT_PUMP_FAILSAFE_SECONDS,
    DEFAULT_TEMPERATURE_UNIT,
    DOMAIN,
)

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from homeassistant.core import HomeAssistant

    from tests.conftest import FakeDevice

_BLE_LOOKUP = "homeassistant.components.bluetooth.async_ble_device_from_address"
_CREATE_DEVICE = "custom_components.storz_bickel.create_device"
_SETUP_ENTRY = "custom_components.storz_bickel.async_setup_entry"


async def test_options_flow_defaults_and_save(
    hass: HomeAssistant,
    setup_entry: Callable[..., Awaitable[MockConfigEntry]],
    fake_device: FakeDevice,
) -> None:
    """The form shows defaults, and saving stores the options and reloads."""
    entry = await setup_entry()

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    # Defaults are applied when no options are stored yet.
    schema = result["data_schema"]
    assert schema is not None
    assert schema({}) == {
        CONF_TEMPERATURE_UNIT: DEFAULT_TEMPERATURE_UNIT,
        CONF_PUMP_FAILSAFE_ENABLED: DEFAULT_PUMP_FAILSAFE_ENABLED,
        CONF_PUMP_FAILSAFE_SECONDS: DEFAULT_PUMP_FAILSAFE_SECONDS,
        CONF_PUMP_COOLDOWN_ENABLED: DEFAULT_PUMP_COOLDOWN_ENABLED,
        CONF_PUMP_COOLDOWN_SECONDS: DEFAULT_PUMP_COOLDOWN_SECONDS,
    }

    # Saving triggers the entry's update listener, which reloads it.
    with (
        patch(_BLE_LOOKUP, return_value=MagicMock()),
        patch(_CREATE_DEVICE, return_value=fake_device),
    ):
        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={
                CONF_TEMPERATURE_UNIT: UnitOfTemperature.FAHRENHEIT,
                CONF_PUMP_FAILSAFE_ENABLED: True,
                CONF_PUMP_FAILSAFE_SECONDS: 60,
                CONF_PUMP_COOLDOWN_ENABLED: False,
                CONF_PUMP_COOLDOWN_SECONDS: 10,
            },
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.options == {
        CONF_TEMPERATURE_UNIT: UnitOfTemperature.FAHRENHEIT,
        CONF_PUMP_FAILSAFE_ENABLED: True,
        CONF_PUMP_FAILSAFE_SECONDS: 60,
        CONF_PUMP_COOLDOWN_ENABLED: False,
        CONF_PUMP_COOLDOWN_SECONDS: 10,
    }
    assert entry.state is ConfigEntryState.LOADED
    assert entry.runtime_data.coordinator.pump_guard is not None


async def test_options_prefilled_from_existing(
    hass: HomeAssistant, enable_bluetooth: None
) -> None:
    """Stored options are used as the form defaults."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="AA:BB:CC:DD:EE:01",
        data={
            CONF_ADDRESS: "AA:BB:CC:DD:EE:01",
            CONF_DEVICE_TYPE: "volcano",
        },
        options={
            CONF_PUMP_FAILSAFE_ENABLED: False,
            CONF_PUMP_FAILSAFE_SECONDS: 120,
            CONF_PUMP_COOLDOWN_ENABLED: True,
            CONF_PUMP_COOLDOWN_SECONDS: 30,
        },
    )
    entry.add_to_hass(hass)
    with patch(_SETUP_ENTRY, return_value=True):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM

    schema = result["data_schema"]
    assert schema is not None
    assert schema({}) == {
        CONF_TEMPERATURE_UNIT: DEFAULT_TEMPERATURE_UNIT,
        CONF_PUMP_FAILSAFE_ENABLED: False,
        CONF_PUMP_FAILSAFE_SECONDS: 120,
        CONF_PUMP_COOLDOWN_ENABLED: True,
        CONF_PUMP_COOLDOWN_SECONDS: 30,
    }


async def test_options_form_shows_for_non_pump_device(
    hass: HomeAssistant, enable_bluetooth: None
) -> None:
    """Devices without a pump (e.g. Crafty) still get the temperature unit option."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="11:22:33:44:55:66",
        data={
            CONF_ADDRESS: "11:22:33:44:55:66",
            CONF_DEVICE_TYPE: "crafty",
        },
    )
    entry.add_to_hass(hass)
    with patch(_SETUP_ENTRY, return_value=True):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    schema = result["data_schema"]
    assert schema is not None
    assert schema({}) == {CONF_TEMPERATURE_UNIT: DEFAULT_TEMPERATURE_UNIT}
