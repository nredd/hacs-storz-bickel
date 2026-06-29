# Examples

Ready-to-use automations and dashboard cards for the Storz & Bickel integration.

> **Entity IDs are placeholders.** These examples use a `volcano` / `venty` prefix. Your entity IDs
> are derived from your device's Bluetooth name — check **Developer Tools → States** for the real
> ones and substitute accordingly. Some entities only exist on certain models (e.g. the pump is
> Volcano-only; battery is on the portable models) — see [CONFIGURATION.md](CONFIGURATION.md).

## Automations

### Notify when the chamber reaches temperature

Fires when the live chamber temperature catches up to the heater setpoint.

```yaml
automation:
  - alias: "Vaporizer reached temperature"
    triggers:
      - trigger: template
        value_template: >
          {{ state_attr('climate.volcano', 'current_temperature') | float(0)
             >= state_attr('climate.volcano', 'temperature') | float(999) }}
    conditions:
      - condition: state
        entity_id: climate.volcano
        state: heat
    actions:
      - action: notify.mobile_app_phone
        data:
          message: >
            Volcano has reached {{ state_attr('climate.volcano', 'temperature') }}°C.
```

### Volcano: run the pump briefly when ready

Turns the pump on for 30 seconds once the setpoint is reached (Volcano only — it's the only model
with a pump).

```yaml
automation:
  - alias: "Volcano auto-pump when ready"
    triggers:
      - trigger: template
        value_template: >
          {{ state_attr('climate.volcano', 'current_temperature') | float(0)
             >= state_attr('climate.volcano', 'temperature') | float(999) }}
    conditions:
      - condition: state
        entity_id: climate.volcano
        state: heat
    actions:
      - action: switch.turn_on
        target:
          entity_id: switch.volcano_pump
      - delay: "00:00:30"
      - action: switch.turn_off
        target:
          entity_id: switch.volcano_pump
```

### Turn the heater off when everyone leaves

Avoids leaving the heater running. Replace `binary_sensor.anyone_home` with your presence entity.

```yaml
automation:
  - alias: "Turn off vaporizer when away"
    triggers:
      - trigger: state
        entity_id: binary_sensor.anyone_home
        to: "off"
    actions:
      - action: climate.turn_off
        target:
          entity_id: climate.volcano
```

### Low-battery notification (portable models)

For Venty / Veazy / Crafty, which report a battery level.

```yaml
automation:
  - alias: "Vaporizer low battery"
    triggers:
      - trigger: numeric_state
        entity_id: sensor.venty_battery
        below: 20
    actions:
      - action: notify.mobile_app_phone
        data:
          message: "Venty battery is low ({{ states('sensor.venty_battery') }}%)."
```

## Dashboard cards

### Thermostat card

The heater is a `climate` entity, so the standard thermostat card works directly.

```yaml
type: thermostat
entity: climate.volcano
```

### Device overview (entities card)

Group the controls you use most. Drop any rows that don't exist on your model.

```yaml
type: entities
title: Volcano
entities:
  - entity: climate.volcano
  - entity: switch.volcano_heater
  - entity: switch.volcano_pump
  - entity: number.volcano_auto_shutoff_timer
  - entity: sensor.volcano_temperature
  - entity: binary_sensor.volcano_heating
```

### Battery gauge (portable models)

```yaml
type: gauge
entity: sensor.venty_battery
name: Battery
unit: "%"
min: 0
max: 100
severity:
  green: 50
  yellow: 20
  red: 0
```

### Temperature history

```yaml
type: history-graph
title: Chamber temperature
hours_to_show: 6
entities:
  - entity: sensor.volcano_temperature
```
