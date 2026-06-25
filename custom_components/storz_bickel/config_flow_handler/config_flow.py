"""Config flow for the Storz & Bickel integration.

Supports Bluetooth auto-discovery (the device advertises and Home Assistant
offers it) and manual setup (pick from nearby discovered devices). There are no
credentials, so there is no reauth step; the BLE address is the unique ID.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_ADDRESS
import voluptuous as vol

from custom_components.storz_bickel.api import detect_device_type
from custom_components.storz_bickel.const import CONF_DEVICE_TYPE, DOMAIN

if TYPE_CHECKING:
    from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
    from homeassistant.config_entries import ConfigFlowResult

    from custom_components.storz_bickel.api import DeviceType


class StorzBickelConfigFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle the config flow for Storz & Bickel devices."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the flow's discovery state."""
        self._discovery_info: BluetoothServiceInfoBleak | None = None
        self._device_type: DeviceType | None = None
        # address -> (advertised name, detected device type)
        self._discovered: dict[str, tuple[str | None, DeviceType]] = {}

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> ConfigFlowResult:
        """Handle a device discovered over Bluetooth."""
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()

        device_type = detect_device_type(
            discovery_info.name, discovery_info.service_uuids
        )
        if device_type is None:
            return self.async_abort(reason="not_supported")

        self._discovery_info = discovery_info
        self._device_type = device_type
        self.context["title_placeholders"] = {
            "name": discovery_info.name or device_type.model_name
        }
        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(
        self,
        user_input: dict[str, object] | None = None,
    ) -> ConfigFlowResult:
        """Confirm setup of a Bluetooth-discovered device."""
        if self._discovery_info is None or self._device_type is None:
            return self.async_abort(reason="not_supported")

        name = self._discovery_info.name or self._device_type.model_name
        if user_input is not None:
            return self._create_entry(
                self._discovery_info.address, self._discovery_info.name, self._device_type
            )

        self._set_confirm_only()
        return self.async_show_form(
            step_id="bluetooth_confirm",
            description_placeholders={"name": name},
        )

    async def async_step_user(
        self, user_input: dict[str, str] | None = None
    ) -> ConfigFlowResult:
        """Handle manual setup by selecting a nearby device."""
        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            name, device_type = self._discovered[address]
            await self.async_set_unique_id(address, raise_on_progress=False)
            self._abort_if_unique_id_configured()
            return self._create_entry(address, name, device_type)

        configured = self._async_current_ids()
        self._discovered = {}
        for info in bluetooth.async_discovered_service_info(self.hass, connectable=True):
            if info.address in configured:
                continue
            device_type = detect_device_type(info.name, info.service_uuids)
            if device_type is not None:
                self._discovered[info.address] = (info.name, device_type)

        if not self._discovered:
            return self.async_abort(reason="no_devices_found")

        options = {
            address: f"{name or device_type.model_name} ({address})"
            for address, (name, device_type) in self._discovered.items()
        }
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_ADDRESS): vol.In(options)}),
        )

    def _create_entry(
        self, address: str, name: str | None, device_type: DeviceType
    ) -> ConfigFlowResult:
        """Create the config entry for a selected device."""
        return self.async_create_entry(
            title=name or device_type.model_name,
            data={CONF_ADDRESS: address, CONF_DEVICE_TYPE: device_type.value},
        )
