"""Climate platform for the Storz & Bickel heater."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityDescription,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature

from custom_components.storz_bickel.const import PARALLEL_UPDATES as _PARALLEL_UPDATES
from custom_components.storz_bickel.entity import StorzBickelEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

    from custom_components.storz_bickel.coordinator import (
        StorzBickelDataUpdateCoordinator,
    )
    from custom_components.storz_bickel.data import StorzBickelConfigEntry

PARALLEL_UPDATES = _PARALLEL_UPDATES


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: StorzBickelConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the heater climate entity."""
    async_add_entities([StorzBickelClimate(entry.runtime_data.coordinator)])


class StorzBickelClimate(StorzBickelEntity, ClimateEntity):
    """The vaporizer heater as a climate entity (heat/off + target temperature)."""

    _attr_name = None
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )
    _enable_turn_on_off_backwards_compatibility = False

    def __init__(self, coordinator: StorzBickelDataUpdateCoordinator) -> None:
        """Initialize the climate entity with device-specific temperature limits."""
        super().__init__(coordinator, ClimateEntityDescription(key="heater"))
        device = coordinator.device
        self._attr_min_temp = device.temp_min
        self._attr_max_temp = device.temp_max
        self._attr_target_temperature_step = device.temp_step

    @property
    def current_temperature(self) -> float | None:
        """Return the current chamber temperature."""
        return self.data.current_temperature

    @property
    def target_temperature(self) -> float | None:
        """Return the heater setpoint."""
        return self.data.target_temperature

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return whether the heater is on (HEAT) or off."""
        if self.data.heater_on is None:
            return None
        return HVACMode.HEAT if self.data.heater_on else HVACMode.OFF

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set a new heater target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is not None:
            await self.device.async_set_target_temperature(float(temperature))

    async def async_turn_on(self) -> None:
        """Turn the heater on."""
        await self.device.async_set_heater(on=True)

    async def async_turn_off(self) -> None:
        """Turn the heater off."""
        await self.device.async_set_heater(on=False)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Turn the heater on or off."""
        await self.device.async_set_heater(on=hvac_mode == HVACMode.HEAT)
