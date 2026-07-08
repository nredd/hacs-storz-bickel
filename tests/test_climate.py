"""Tests for the climate entity, including the Fahrenheit display override."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.helpers import entity_platform, entity_registry as er

from custom_components.storz_bickel.climate import StorzBickelClimate
from custom_components.storz_bickel.const import CONF_TEMPERATURE_UNIT, DOMAIN

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from homeassistant.core import HomeAssistant
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    from tests.conftest import FakeDevice


def _climate_entity_id(hass: HomeAssistant, fake_device: FakeDevice) -> str:
    """Look up the climate entity's ID from the registry."""
    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id(
        "climate", DOMAIN, f"{fake_device.address}_heater"
    )
    assert entity_id is not None
    return entity_id


def _climate_entity(hass: HomeAssistant, fake_device: FakeDevice) -> StorzBickelClimate:
    """Return the live climate entity object (not the display-converted state).

    State attributes go through Home Assistant's ``show_temp`` display
    conversion against the system unit, which would mask the entity's own
    Fahrenheit-option conversion under test; read the entity's properties
    directly instead.
    """
    entity_id = _climate_entity_id(hass, fake_device)
    for platform in entity_platform.async_get_platforms(hass, DOMAIN):
        if platform.domain == "climate" and entity_id in platform.entities:
            entity = platform.entities[entity_id]
            assert isinstance(entity, StorzBickelClimate)
            return entity
    raise AssertionError(f"Climate entity {entity_id} not found in any platform")


async def test_default_celsius_passthrough(
    hass: HomeAssistant,
    setup_entry: Callable[..., Awaitable[MockConfigEntry]],
    fake_device: FakeDevice,
) -> None:
    """With no option set, the climate entity displays raw Celsius values."""
    await setup_entry()
    entity = _climate_entity(hass, fake_device)

    assert entity.temperature_unit == UnitOfTemperature.CELSIUS
    assert entity.target_temperature == fake_device.state.target_temperature
    assert entity.current_temperature == fake_device.state.current_temperature
    assert entity.min_temp == fake_device.temp_min
    assert entity.max_temp == fake_device.temp_max
    assert entity.target_temperature_step == fake_device.temp_step


async def test_fahrenheit_option_converts_display_values(
    hass: HomeAssistant,
    setup_entry: Callable[..., Awaitable[MockConfigEntry]],
    fake_device: FakeDevice,
) -> None:
    """The Fahrenheit option converts current/target/min/max and the step size."""
    fake_device.state.current_temperature = 100.0
    fake_device.state.target_temperature = 100.0
    await setup_entry(options={CONF_TEMPERATURE_UNIT: UnitOfTemperature.FAHRENHEIT})
    entity = _climate_entity(hass, fake_device)

    assert entity.temperature_unit == UnitOfTemperature.FAHRENHEIT
    # 100C -> 212F (absolute conversion).
    assert entity.current_temperature == 212.0
    assert entity.target_temperature == 212.0
    # The 1.0C step must go through the interval path (1.8), not the absolute
    # affine transform (which would give 33.8).
    assert entity.target_temperature_step == 1.8


async def test_set_temperature_converts_fahrenheit_input_to_celsius(
    hass: HomeAssistant,
    setup_entry: Callable[..., Awaitable[MockConfigEntry]],
    fake_device: FakeDevice,
) -> None:
    """Setting a target temperature in Fahrenheit mode is converted back to Celsius.

    Calls the entity method directly rather than the ``climate.set_temperature``
    service: the service layer applies its own conversion from Home
    Assistant's system unit before invoking the entity, which would be a
    second, unrelated conversion layered on top of the one under test here.
    """
    await setup_entry(options={CONF_TEMPERATURE_UNIT: UnitOfTemperature.FAHRENHEIT})
    entity = _climate_entity(hass, fake_device)

    await entity.async_set_temperature(**{ATTR_TEMPERATURE: 212.0})
    assert fake_device.target_temperature_calls == [100.0]
