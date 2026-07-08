"""Options flow for per-device pump protections.

Exposes enable toggles and durations for the pump failsafe window (auto-off
after a configurable run time) and the post-off cooldown (minimum wait before
the pump may be turned back on). Saving options triggers the entry's update
listener, which reloads the entry so the coordinator picks up the new values.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.config_entries import OptionsFlow
from homeassistant.const import UnitOfTemperature, UnitOfTime
from homeassistant.helpers.selector import (
    BooleanSelector,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
)
import voluptuous as vol

from custom_components.storz_bickel.api import DeviceType, capabilities_for
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
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigFlowResult

MAX_PUMP_FAILSAFE_SECONDS = 600
MAX_PUMP_COOLDOWN_SECONDS = 300


def _duration_selector(max_seconds: int) -> vol.All:
    """Return a boxed seconds input constrained to ``[1, max_seconds]``.

    Wraps the selector in ``vol.Coerce(int)`` because ``NumberSelector``
    validates to ``float``.
    """
    selector = NumberSelector(
        NumberSelectorConfig(
            min=1,
            max=max_seconds,
            step=1,
            unit_of_measurement=UnitOfTime.SECONDS,
            mode=NumberSelectorMode.BOX,
        )
    )
    return vol.All(selector, vol.Coerce(int))


class StorzBickelOptionsFlowHandler(OptionsFlow):
    """Handle per-entry options for Storz & Bickel devices."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Show and process the device options (temperature unit, pump protections)."""
        device_type = DeviceType(self.config_entry.data[CONF_DEVICE_TYPE])

        if user_input is not None:
            return self.async_create_entry(data=user_input)

        options = self.config_entry.options
        schema_dict: dict[vol.Marker, Any] = {
            vol.Required(
                CONF_TEMPERATURE_UNIT,
                default=options.get(CONF_TEMPERATURE_UNIT, DEFAULT_TEMPERATURE_UNIT),
            ): SelectSelector(
                SelectSelectorConfig(
                    options=[UnitOfTemperature.CELSIUS, UnitOfTemperature.FAHRENHEIT]
                )
            ),
        }
        if capabilities_for(device_type).pump:
            schema_dict.update(
                {
                    vol.Required(
                        CONF_PUMP_FAILSAFE_ENABLED,
                        default=options.get(
                            CONF_PUMP_FAILSAFE_ENABLED, DEFAULT_PUMP_FAILSAFE_ENABLED
                        ),
                    ): BooleanSelector(),
                    vol.Required(
                        CONF_PUMP_FAILSAFE_SECONDS,
                        default=options.get(
                            CONF_PUMP_FAILSAFE_SECONDS, DEFAULT_PUMP_FAILSAFE_SECONDS
                        ),
                    ): _duration_selector(MAX_PUMP_FAILSAFE_SECONDS),
                    vol.Required(
                        CONF_PUMP_COOLDOWN_ENABLED,
                        default=options.get(
                            CONF_PUMP_COOLDOWN_ENABLED, DEFAULT_PUMP_COOLDOWN_ENABLED
                        ),
                    ): BooleanSelector(),
                    vol.Required(
                        CONF_PUMP_COOLDOWN_SECONDS,
                        default=options.get(
                            CONF_PUMP_COOLDOWN_SECONDS, DEFAULT_PUMP_COOLDOWN_SECONDS
                        ),
                    ): _duration_selector(MAX_PUMP_COOLDOWN_SECONDS),
                }
            )
        return self.async_show_form(step_id="init", data_schema=vol.Schema(schema_dict))
