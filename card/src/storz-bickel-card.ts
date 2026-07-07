/**
 * `<storz-bickel-card>` — companion Lovelace card for the Storz & Bickel
 * integration.
 *
 * Configured with a device registry id; every entity is derived from the
 * registry (see entities.ts), so the card adapts to each device's
 * capabilities: pump bar on the Volcano, battery chip on portables, boost
 * and vibration rows only where supported.
 */

import { html, LitElement, nothing } from "lit";
import { property, state } from "lit/decorators.js";
import { CARD_TAG, CARD_VERSION, DEFAULT_PRESETS, DIAL_TAG, EDITOR_TAG } from "./const";
import { SbTempDial } from "./dial";
import { StorzBickelCardEditor } from "./editor";
import { type DeviceEntityIds, deviceEntities } from "./entities";
import { cardStyles } from "./styles";
import type { CardConfig, HassEntity, HomeAssistant, LovelaceCardEditor } from "./types";

/** Climate attributes the card reads (all set by the integration). */
interface ClimateAttributes {
  currentTemperature?: number;
  targetTemperature?: number;
  minTemp: number;
  maxTemp: number;
  targetTempStep: number;
  hvacAction?: string;
}

function asNumber(value: unknown): number | undefined {
  const parsed = typeof value === "string" ? Number(value) : value;
  return typeof parsed === "number" && Number.isFinite(parsed) ? parsed : undefined;
}

function climateAttributes(entity: HassEntity): ClimateAttributes {
  return {
    currentTemperature: asNumber(entity.attributes.current_temperature),
    targetTemperature: asNumber(entity.attributes.temperature),
    minTemp: asNumber(entity.attributes.min_temp) ?? 40,
    maxTemp: asNumber(entity.attributes.max_temp) ?? 230,
    targetTempStep: asNumber(entity.attributes.target_temp_step) ?? 1,
    hvacAction:
      typeof entity.attributes.hvac_action === "string" ? entity.attributes.hvac_action : undefined,
  };
}

/** Companion card for Storz & Bickel vaporizers. */
export class StorzBickelCard extends LitElement {
  /** The Home Assistant state object, set by Lovelace on every update. */
  @property({ attribute: false }) hass?: HomeAssistant;

  @state() private config?: CardConfig;

  /** Optimistic target shown while stepper taps are being debounced. */
  @state() private pendingTarget?: number;

  /** Debounce window for stepper taps before calling the service (ms). */
  debounceMs = 500;

  private debounceTimer?: ReturnType<typeof setTimeout>;

  static override styles = cardStyles;

  /** Lovelace: provide the visual config editor. */
  static getConfigElement(): LovelaceCardEditor {
    return document.createElement(EDITOR_TAG) as LovelaceCardEditor;
  }

  /** Lovelace: seed the card picker with the first configured device. */
  static getStubConfig(hass?: HomeAssistant): Record<string, unknown> {
    const entry = hass
      ? Object.values(hass.entities).find(
          (candidate) => candidate.platform === "storz_bickel" && candidate.device_id,
        )
      : undefined;
    return { device: entry?.device_id ?? "", presets: [...DEFAULT_PRESETS] };
  }

  /** Lovelace: validate and store the card configuration. */
  setConfig(config: CardConfig): void {
    if (!config.device) {
      throw new Error("storz-bickel-card: 'device' is required (a Storz & Bickel device)");
    }
    this.config = config;
  }

  /** Lovelace: approximate masonry height in rows. */
  getCardSize(): number {
    return 5;
  }

  /** Lovelace: sizing hints for sections view. */
  getGridOptions(): Record<string, number> {
    return { columns: 12, rows: 8, min_columns: 6, min_rows: 6 };
  }

  private get entityIds(): DeviceEntityIds {
    if (!this.hass || !this.config) {
      return {};
    }
    return deviceEntities(this.hass, this.config.device);
  }

  private entityState(entityId?: string): HassEntity | undefined {
    return entityId ? this.hass?.states[entityId] : undefined;
  }

  private callService(domain: string, service: string, data: Record<string, unknown>): void {
    this.hass?.callService(domain, service, data);
  }

  private setTargetTemperature(entityId: string, temperature: number): void {
    this.callService("climate", "set_temperature", { entity_id: entityId, temperature });
  }

  private handleDialStep(direction: number, climate: HassEntity): void {
    const attrs = climateAttributes(climate);
    const base = this.pendingTarget ?? attrs.targetTemperature ?? attrs.minTemp;
    const next = Math.min(
      attrs.maxTemp,
      Math.max(attrs.minTemp, base + direction * attrs.targetTempStep),
    );
    this.pendingTarget = next;
    clearTimeout(this.debounceTimer);
    this.debounceTimer = setTimeout(() => {
      this.pendingTarget = undefined;
      this.setTargetTemperature(climate.entity_id, next);
    }, this.debounceMs);
  }

  private handlePreset(temperature: number, climate: HassEntity): void {
    const attrs = climateAttributes(climate);
    const clamped = Math.min(attrs.maxTemp, Math.max(attrs.minTemp, temperature));
    clearTimeout(this.debounceTimer);
    this.pendingTarget = clamped;
    this.setTargetTemperature(climate.entity_id, clamped);
  }

  private toggleHeat(climate: HassEntity): void {
    this.callService("climate", "set_hvac_mode", {
      entity_id: climate.entity_id,
      hvac_mode: climate.state === "heat" ? "off" : "heat",
    });
  }

  private toggleSwitch(entity: HassEntity): void {
    this.callService("switch", entity.state === "on" ? "turn_off" : "turn_on", {
      entity_id: entity.entity_id,
    });
  }

  private setNumber(entityId: string, value: number): void {
    this.callService("number", "set_value", { entity_id: entityId, value });
  }

  protected override render() {
    if (!this.hass || !this.config) {
      return nothing;
    }
    const ids = this.entityIds;
    const climate = this.entityState(ids.climate);
    if (!climate) {
      return html`<ha-card><div class="body">Device entities not found.</div></ha-card>`;
    }

    const attrs = climateAttributes(climate);
    const connection = this.entityState(ids.connection);
    const connected = connection ? connection.state === "on" : true;
    const heaterOn = climate.state === "heat";
    const heating = attrs.hvacAction === "heating";
    const target = this.pendingTarget ?? attrs.targetTemperature;
    const battery = this.entityState(ids.battery);
    const pump = this.entityState(ids.pump);
    const unit = this.hass.config.unit_system.temperature;
    const device = this.hass.devices[this.config.device];
    const name = this.config.name ?? device?.name_by_user ?? device?.name ?? "Storz & Bickel";
    const presets = this.config.presets ?? [];

    return html`
      <ha-card>
        <div class="body ${connected ? "" : "disconnected"}">
          <div class="header">
            <span class="name">${name}</span>
            ${
              battery && asNumber(battery.state) !== undefined
                ? html`<span class="battery">🔋 ${Math.round(asNumber(battery.state) ?? 0)}%</span>`
                : nothing
            }
            <span
              class="dot ${connected ? "connected" : "disconnected"}"
              title=${connected ? "Connected" : "Disconnected"}
            ></span>
          </div>
          <div class="controls">
            <sb-temp-dial
              .current=${attrs.currentTemperature}
              .target=${target}
              .min=${attrs.minTemp}
              .max=${attrs.maxTemp}
              .unit=${unit}
              ?active=${heaterOn}
              ?heating=${heating}
              ?disabled=${!connected}
              @dial-step=${(event: CustomEvent<{ direction: number }>) =>
                this.handleDialStep(event.detail.direction, climate)}
            ></sb-temp-dial>
            <button class="heat ${heaterOn ? "on" : ""}" @click=${() => this.toggleHeat(climate)}>
              ⏻ Heat
            </button>
            ${
              presets.length > 0
                ? html`
                  <div class="presets">
                    ${presets.map(
                      (preset) => html`
                        <button
                          class="preset ${target !== undefined && Math.round(target) === Math.round(preset) ? "active" : ""}"
                          @click=${() => this.handlePreset(preset, climate)}
                        >
                          ${preset}${unit}
                        </button>
                      `,
                    )}
                  </div>
                `
                : nothing
            }
            ${
              pump
                ? html`
                  <button
                    class="pump ${pump.state === "on" ? "on" : ""}"
                    @click=${() => this.toggleSwitch(pump)}
                  >
                    ${pump.state === "on" ? "≋ Pump ≋" : "Pump"}
                  </button>
                `
                : nothing
            }
            ${this.renderStatus(ids)} ${this.renderSettings(ids)}
          </div>
        </div>
      </ha-card>
    `;
  }

  private renderStatus(ids: DeviceEntityIds) {
    const autoShutoff = this.entityState(ids.autoShutoffEnabled);
    const minutes = this.entityState(ids.autoShutoffMinutes);
    if (!autoShutoff && !minutes) {
      return nothing;
    }
    const enabled = autoShutoff ? autoShutoff.state === "on" : true;
    const minutesValue = minutes ? asNumber(minutes.state) : undefined;
    return html`
      <div class="status">
        <span>Auto shutoff:</span>
        <span>
          ${enabled ? (minutesValue !== undefined ? `${minutesValue} min` : "on") : "off"}
        </span>
      </div>
    `;
  }

  private renderSettings(ids: DeviceEntityIds) {
    const led = this.entityState(ids.ledBrightness);
    const minutes = this.entityState(ids.autoShutoffMinutes);
    const boost = this.entityState(ids.boostTemperature);
    const vibration = this.entityState(ids.vibration);
    if (!led && !minutes && !boost && !vibration) {
      return nothing;
    }
    return html`
      <details class="settings">
        <summary>Settings</summary>
        ${led ? this.renderNumberRow("LED brightness", led, "%") : nothing}
        ${minutes ? this.renderNumberRow("Auto shutoff", minutes, " min") : nothing}
        ${boost ? this.renderNumberRow("Boost", boost, "°") : nothing}
        ${
          vibration
            ? html`
              <div class="row">
                <label for="vibration">Vibration</label>
                <input
                  id="vibration"
                  type="checkbox"
                  .checked=${vibration.state === "on"}
                  @change=${() => this.toggleSwitch(vibration)}
                />
              </div>
            `
            : nothing
        }
      </details>
    `;
  }

  private renderNumberRow(label: string, entity: HassEntity, suffix: string) {
    const value = asNumber(entity.state);
    const min = asNumber(entity.attributes.min) ?? 0;
    const max = asNumber(entity.attributes.max) ?? 100;
    const step = asNumber(entity.attributes.step) ?? 1;
    const id = entity.entity_id.replaceAll(".", "-");
    return html`
      <div class="row">
        <label for=${id}>${label}</label>
        <input
          id=${id}
          type="range"
          min=${min}
          max=${max}
          step=${step}
          .value=${String(value ?? min)}
          @change=${(event: Event) =>
            this.setNumber(entity.entity_id, Number((event.target as HTMLInputElement).value))}
        />
        <span class="value">${value ?? "—"}${suffix}</span>
      </div>
    `;
  }
}

if (!customElements.get(DIAL_TAG)) {
  customElements.define(DIAL_TAG, SbTempDial);
}
if (!customElements.get(CARD_TAG)) {
  customElements.define(CARD_TAG, StorzBickelCard);
}
if (!customElements.get(EDITOR_TAG)) {
  customElements.define(EDITOR_TAG, StorzBickelCardEditor);
}

window.customCards = window.customCards ?? [];
if (!window.customCards.some((card) => card.type === CARD_TAG)) {
  window.customCards.push({
    type: CARD_TAG,
    name: "Storz & Bickel Card",
    description: "Controls for Storz & Bickel vaporizers (Volcano, Venty, Veazy, Crafty).",
    preview: true,
    documentationURL: "https://github.com/nredd/hacs-storz-bickel",
  });
}

console.info(
  `%c STORZ-BICKEL-CARD %c v${CARD_VERSION} `,
  "background: #ff9800; color: #fff; font-weight: 600; border-radius: 3px 0 0 3px;",
  "background: #424242; color: #fff; border-radius: 0 3px 3px 0;",
);
