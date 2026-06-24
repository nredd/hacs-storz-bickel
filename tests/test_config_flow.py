"""Config flow tests for the Storz & Bickel integration."""

from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING
from unittest.mock import patch

from homeassistant.config_entries import SOURCE_BLUETOOTH, SOURCE_USER
from homeassistant.const import CONF_ADDRESS
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.storz_bickel.api import const as c
from custom_components.storz_bickel.const import CONF_DEVICE_TYPE, DOMAIN

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

VOLCANO_ADDRESS = "AA:BB:CC:DD:EE:FF"
CRAFTY_ADDRESS = "11:22:33:44:55:66"

_SETUP_ENTRY = "custom_components.storz_bickel.async_setup_entry"
_DISCOVERED = "custom_components.storz_bickel.config_flow_handler.config_flow.bluetooth.async_discovered_service_info"


def _info(address: str, name: str | None, service_uuids: list[str] | None = None) -> SimpleNamespace:
    """Build a lightweight discovery info object exposing the fields the flow uses."""
    return SimpleNamespace(address=address, name=name, service_uuids=service_uuids or [])


async def test_bluetooth_discovery_creates_entry(hass: HomeAssistant, enable_bluetooth: None) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_BLUETOOTH},
        data=_info(VOLCANO_ADDRESS, "S&B VOLCANO H"),
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "bluetooth_confirm"

    with patch(_SETUP_ENTRY, return_value=True):
        result = await hass.config_entries.flow.async_configure(result["flow_id"], {})

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "S&B VOLCANO H"
    assert result["data"] == {CONF_ADDRESS: VOLCANO_ADDRESS, CONF_DEVICE_TYPE: "volcano"}
    assert result["result"].unique_id == VOLCANO_ADDRESS


async def test_bluetooth_discovery_not_supported(hass: HomeAssistant, enable_bluetooth: None) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_BLUETOOTH},
        data=_info("99:99:99:99:99:99", "Some Other Device", ["1234"]),
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "not_supported"


async def test_bluetooth_discovery_already_configured(hass: HomeAssistant, enable_bluetooth: None) -> None:
    entry = MockConfigEntry(domain=DOMAIN, unique_id=VOLCANO_ADDRESS)
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_BLUETOOTH},
        data=_info(VOLCANO_ADDRESS, "S&B VOLCANO H"),
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_user_flow_no_devices(hass: HomeAssistant, enable_bluetooth: None) -> None:
    with patch(_DISCOVERED, return_value=[]):
        result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "no_devices_found"


async def test_user_flow_selects_device(hass: HomeAssistant, enable_bluetooth: None) -> None:
    discovered = [_info(CRAFTY_ADDRESS, None, [c.CRAFTY_SERVICE_DATA])]
    with patch(_DISCOVERED, return_value=discovered):
        result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})
        assert result["type"] is FlowResultType.FORM
        assert result["step_id"] == "user"

        with patch(_SETUP_ENTRY, return_value=True):
            result = await hass.config_entries.flow.async_configure(
                result["flow_id"],
                {CONF_ADDRESS: CRAFTY_ADDRESS},
            )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {CONF_ADDRESS: CRAFTY_ADDRESS, CONF_DEVICE_TYPE: "crafty"}
