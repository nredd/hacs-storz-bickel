"""GATT service/characteristic UUIDs and protocol constants for Storz & Bickel devices.

The Volcano Hybrid map is validated against real hardware and corroborated by two
independent projects (the MIT-licensed ``Chuffnugget/volcano_integration`` Home
Assistant component and the ``firsttris/reactive-volcano-app`` web app). The
Venty/Veazy and Crafty maps are derived from the reverse-engineered web app and
are pending hardware validation in this repository.

UUID facts (and the byte encodings documented alongside them) are protocol facts,
not copyrightable expression; the parsing logic in this package is an original
Python implementation.
"""

from __future__ import annotations

from typing import Final

# --------------------------------------------------------------------------- #
# Volcano Hybrid  (base UUID suffix ...-5354-4f52-5a26-4249434b454c)
# --------------------------------------------------------------------------- #
VOLCANO_SERVICE_DEVICE_STATE: Final = "10100000-5354-4f52-5a26-4249434b454c"
VOLCANO_SERVICE_DEVICE_CONTROL: Final = "10110000-5354-4f52-5a26-4249434b454c"

VOLCANO_UUID_CURRENT_TEMP: Final = "10110001-5354-4f52-5a26-4249434b454c"
VOLCANO_UUID_TARGET_TEMP: Final = "10110003-5354-4f52-5a26-4249434b454c"
VOLCANO_UUID_HEAT_ON: Final = "1011000f-5354-4f52-5a26-4249434b454c"
VOLCANO_UUID_HEAT_OFF: Final = "10110010-5354-4f52-5a26-4249434b454c"
VOLCANO_UUID_PUMP_ON: Final = "10110013-5354-4f52-5a26-4249434b454c"
VOLCANO_UUID_PUMP_OFF: Final = "10110014-5354-4f52-5a26-4249434b454c"
# Status register: notifies heat/pump state as a byte pair (see VOLCANO_STATUS_PATTERNS).
VOLCANO_UUID_STATUS_REGISTER: Final = "1010000c-5354-4f52-5a26-4249434b454c"
# Control register: uint32 LE bitmask carrying display/vibration flags (read-modify-write).
VOLCANO_UUID_CONTROL_REGISTER: Final = "1010000e-5354-4f52-5a26-4249434b454c"
VOLCANO_UUID_LED_BRIGHTNESS: Final = "10110005-5354-4f52-5a26-4249434b454c"
VOLCANO_UUID_AUTO_OFF_ENABLE: Final = "1011000c-5354-4f52-5a26-4249434b454c"
VOLCANO_UUID_AUTO_OFF_SETTING: Final = "1011000d-5354-4f52-5a26-4249434b454c"
VOLCANO_UUID_HOURS_OF_OPERATION: Final = "10110015-5354-4f52-5a26-4249434b454c"
VOLCANO_UUID_MINUTES_OF_OPERATION: Final = "10110016-5354-4f52-5a26-4249434b454c"
VOLCANO_UUID_SERIAL_NUMBER: Final = "10100008-5354-4f52-5a26-4249434b454c"
VOLCANO_UUID_FIRMWARE_VERSION: Final = "10100003-5354-4f52-5a26-4249434b454c"
VOLCANO_UUID_BLE_FIRMWARE_VERSION: Final = "10100004-5354-4f52-5a26-4249434b454c"

# Status-register bit masks (uint16 LE, characteristic 1010000c). The byte-pair
# values reported by some firmwares decode identically under these masks
# (e.g. heat+pump 0x3023 -> heater 0x0020 set, pump 0x2000 set).
VOLCANO_STATUS_MASK_HEATER: Final = 0x0020
VOLCANO_STATUS_MASK_PUMP: Final = 0x2000
VOLCANO_STATUS_MASK_AUTO_SHUTOFF: Final = 0x0200

# Control-register bit masks (uint32 LE, characteristic 1010000e).
VOLCANO_MASK_VIBRATION: Final = 0x0400
VOLCANO_MASK_DISPLAY_ON_COOLING: Final = 0x1000
VOLCANO_MASK_FAHRENHEIT: Final = 0x0200

# Heat/pump "trigger" characteristics expect a single zero byte (matches the
# Storz & Bickel web app's writeValue(uint8(0))).
VOLCANO_TRIGGER_PAYLOAD: Final = b"\x00"

# --------------------------------------------------------------------------- #
# Venty / Veazy  (base UUID suffix ...-5354-4f52-5a26-4249434b454c)
# Single control characteristic using a write-mask / packed-status protocol.
# --------------------------------------------------------------------------- #
VENTY_SERVICE_PRIMARY: Final = "00000000-5354-4f52-5a26-4249434b454c"
VENTY_UUID_CONTROL: Final = "00000001-5354-4f52-5a26-4249434b454c"
VENTY_UUID_DEVICE_NAME: Final = "00002a00-0000-1000-8000-00805f9b34fb"

# Control-characteristic command opcodes (byte 0 of the 20-byte frame; the same
# opcode is echoed in byte 0 of the notification response).
VENTY_CMD_STATUS: Final = 0x01
VENTY_CMD_EXTENDED_DATA: Final = (
    0x04  # -> heater runtime + battery charging time (uint24 each)
)
VENTY_CMD_DEVICE_DATA: Final = 0x05  # -> serial number

# Write masks (byte 1 of the frame) selecting which fields the write updates.
VENTY_WRITE_SET_TEMPERATURE: Final = 1 << 1
VENTY_WRITE_SET_BOOST: Final = 1 << 2
VENTY_WRITE_SET_SUPERBOOST: Final = 1 << 3
VENTY_WRITE_AUTO_SHUTOFF: Final = 1 << 4
VENTY_WRITE_HEATER: Final = 1 << 5
VENTY_WRITE_SETTINGS: Final = 1 << 7

# Status-frame byte offsets (notification payload for VENTY_CMD_STATUS).
VENTY_STATUS_TARGET_TEMP_LO: Final = 4  # uint16 LE across bytes 4-5, tenths of a degree
VENTY_STATUS_BOOST_TEMP: Final = 6
VENTY_STATUS_SUPERBOOST_TEMP: Final = 7
VENTY_STATUS_BATTERY: Final = 8
VENTY_STATUS_AUTO_OFF_LO: Final = 9  # uint16 LE across bytes 9-10, seconds
VENTY_STATUS_HEATER_MODE: Final = 11  # 0=off, 1=normal, 2=boost, 3=superboost
VENTY_STATUS_CHARGER: Final = 13  # >0 = charging
VENTY_STATUS_SETTINGS: Final = 14
VENTY_STATUS_MIN_LEN: Final = 15

# Settings byte (offset 14) bit flags.
VENTY_SETTING_UNIT_FAHRENHEIT: Final = 0x01
VENTY_SETTING_SETPOINT_REACHED: Final = 0x02
VENTY_SETTING_VIBRATION: Final = 0x40

# Heater-mode values written to byte 11.
VENTY_HEATER_MODE_OFF: Final = 0
VENTY_HEATER_MODE_NORMAL: Final = 1

# Extended-data frame (VENTY_CMD_EXTENDED_DATA) uint24 LE fields.
VENTY_EXT_HEATER_RUNTIME_OFF: Final = 1  # bytes 1-3
VENTY_EXT_BATTERY_CHARGE_OFF: Final = 4  # bytes 4-6

# --------------------------------------------------------------------------- #
# Crafty  (base UUID suffix ...-4c45-4b43-4942-265a524f5453)
# Per-characteristic protocol.
# --------------------------------------------------------------------------- #
CRAFTY_SERVICE_DATA: Final = "00000001-4c45-4b43-4942-265a524f5453"
CRAFTY_SERVICE_CONTROL: Final = "00000002-4c45-4b43-4942-265a524f5453"
CRAFTY_SERVICE_STATUS: Final = "00000003-4c45-4b43-4942-265a524f5453"

CRAFTY_UUID_CURRENT_TEMP: Final = "00000011-4c45-4b43-4942-265a524f5453"
CRAFTY_UUID_TARGET_TEMP: Final = "00000021-4c45-4b43-4942-265a524f5453"
CRAFTY_UUID_BOOST_TEMP: Final = "00000031-4c45-4b43-4942-265a524f5453"
CRAFTY_UUID_HEAT_ON: Final = "00000081-4c45-4b43-4942-265a524f5453"
CRAFTY_UUID_HEAT_OFF: Final = "00000091-4c45-4b43-4942-265a524f5453"
CRAFTY_UUID_POWER: Final = "00000041-4c45-4b43-4942-265a524f5453"
CRAFTY_UUID_LED_BRIGHTNESS: Final = "00000051-4c45-4b43-4942-265a524f5453"
CRAFTY_UUID_AUTO_OFF_COUNTDOWN: Final = "00000061-4c45-4b43-4942-265a524f5453"
CRAFTY_UUID_AUTO_OFF_CURRENT: Final = "00000071-4c45-4b43-4942-265a524f5453"
CRAFTY_UUID_BATTERY: Final = "00000063-4c45-4b43-4942-265a524f5453"
CRAFTY_UUID_BATTERY2: Final = "00000073-4c45-4b43-4942-265a524f5453"
CRAFTY_UUID_SYSTEM_STATUS: Final = "00000083-4c45-4b43-4942-265a524f5453"
CRAFTY_UUID_USE_HOURS: Final = "00000023-4c45-4b43-4942-265a524f5453"
CRAFTY_UUID_USE_MINUTES: Final = "000001e3-4c45-4b43-4942-265a524f5453"
CRAFTY_UUID_FIRMWARE_VERSION: Final = "00000032-4c45-4b43-4942-265a524f5453"
CRAFTY_UUID_BLE_FIRMWARE_VERSION: Final = "00000072-4c45-4b43-4942-265a524f5453"

# --------------------------------------------------------------------------- #
# Temperature limits (degrees Celsius) per device family.
# --------------------------------------------------------------------------- #
VOLCANO_TEMP_MIN: Final = 40.0
VOLCANO_TEMP_MAX: Final = 230.0
PORTABLE_TEMP_MIN: Final = 40.0
PORTABLE_TEMP_MAX: Final = 210.0

# Temperature is transmitted as tenths of a degree Celsius (uint16 LE).
TEMP_SCALE: Final = 10
