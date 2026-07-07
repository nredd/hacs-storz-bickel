"""Tests for the bundled Lovelace card registration."""

from __future__ import annotations

from pathlib import Path
import re
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

from homeassistant.components.frontend import DATA_EXTRA_MODULE_URL
from homeassistant.components.http import HomeAssistantHTTP, StaticPathConfig
from homeassistant.const import CONF_ADDRESS
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.storz_bickel.api import DeviceType
from custom_components.storz_bickel.const import CARD_URL, CONF_DEVICE_TYPE, DOMAIN
from tests.conftest import BLE_LOOKUP, CREATE_DEVICE, FakeDevice

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Iterator

    from homeassistant.core import HomeAssistant

SECOND_ADDRESS = "AA:BB:CC:DD:EE:00"
CARD_URL_PATTERN = re.compile(rf"^{re.escape(CARD_URL)}\?v=.+$")


@pytest.fixture
def static_path_spy() -> Iterator[Callable[[], list[StaticPathConfig]]]:
    """Spy on all static path registrations, keeping their behavior intact."""
    registered: list[StaticPathConfig] = []
    original = HomeAssistantHTTP.async_register_static_paths

    async def _record(self: HomeAssistantHTTP, configs: list[StaticPathConfig]) -> None:
        registered.extend(configs)
        await original(self, configs)

    with patch.object(HomeAssistantHTTP, "async_register_static_paths", _record):
        yield lambda: [cfg for cfg in registered if cfg.url_path == CARD_URL]


def _card_extra_js_urls(hass: HomeAssistant) -> list[str]:
    """Return the frontend extra module URLs pointing at the bundled card."""
    manager = hass.data[DATA_EXTRA_MODULE_URL]
    return [url for url in manager.urls if CARD_URL_PATTERN.match(url)]


async def _setup_second_entry(hass: HomeAssistant) -> MockConfigEntry:
    """Set up a second Volcano entry backed by its own fake device."""
    device = FakeDevice()
    device.address = SECOND_ADDRESS
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=SECOND_ADDRESS,
        data={CONF_ADDRESS: SECOND_ADDRESS, CONF_DEVICE_TYPE: DeviceType.VOLCANO.value},
    )
    entry.add_to_hass(hass)
    with (
        patch(BLE_LOOKUP, return_value=MagicMock()),
        patch(CREATE_DEVICE, return_value=device),
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    return entry


async def test_card_static_path_registered(
    hass: HomeAssistant,
    setup_entry: Callable[..., Awaitable[MockConfigEntry]],
    static_path_spy: Callable[[], list[StaticPathConfig]],
) -> None:
    """Setup serves the committed card bundle at the expected URL."""
    await setup_entry()

    card_paths = static_path_spy()
    assert len(card_paths) == 1
    assert card_paths[0].url_path == "/storz_bickel/storz-bickel-card.js"
    # Guards against a missing or uncommitted bundle. Blocking I/O is fine in a test.
    assert Path(card_paths[0].path).is_file()  # noqa: ASYNC240


async def test_card_extra_js_url_added(
    hass: HomeAssistant,
    setup_entry: Callable[..., Awaitable[MockConfigEntry]],
) -> None:
    """Setup injects the card into the frontend with a version cache-buster."""
    await setup_entry()

    assert len(_card_extra_js_urls(hass)) == 1


async def test_card_registered_once_across_entries_and_reloads(
    hass: HomeAssistant,
    setup_entry: Callable[..., Awaitable[MockConfigEntry]],
    fake_device: FakeDevice,
    static_path_spy: Callable[[], list[StaticPathConfig]],
) -> None:
    """A second entry and an entry reload do not re-register the card."""
    entry = await setup_entry()
    await _setup_second_entry(hass)

    with (
        patch(BLE_LOOKUP, return_value=MagicMock()),
        patch(CREATE_DEVICE, return_value=fake_device),
    ):
        await hass.config_entries.async_reload(entry.entry_id)
        await hass.async_block_till_done()

    assert len(static_path_spy()) == 1
    assert len(_card_extra_js_urls(hass)) == 1
