/**
 * `<sb-temp-dial>` — the card's hero element: a 270° thermostat-style ring.
 *
 * Renders the current temperature as an animated SVG arc between the climate
 * entity's min/max, a marker dot at the target temperature, and −/+ stepper
 * buttons docked in the ring's bottom gap. Purely presentational: steppers
 * emit `dial-step` events; the card owns service calls and debouncing.
 */

import { css, html, LitElement, nothing, svg } from "lit";
import { property } from "lit/decorators.js";

const CENTER = 100;
const RADIUS = 85;
/** Arc start angle in SVG (y-down) degrees; 135° is the bottom-left. */
const START_ANGLE = 135;
/** Arc sweep in degrees, clockwise through the top to the bottom-right. */
const SWEEP = 270;
/** Normalized path length so dash math is percentage-based. */
const PATH_LENGTH = 100;

/** Point on the ring at `angleDeg` (SVG y-down coordinates). */
function polar(angleDeg: number, radius = RADIUS): { x: number; y: number } {
  const rad = (angleDeg * Math.PI) / 180;
  return { x: CENTER + radius * Math.cos(rad), y: CENTER + radius * Math.sin(rad) };
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

/** Thermostat-style temperature ring with stepper buttons. */
export class SbTempDial extends LitElement {
  /** Current temperature reported by the device. */
  @property({ type: Number }) current?: number;

  /** Target temperature (possibly an optimistic pending value). */
  @property({ type: Number }) target?: number;

  /** Lower bound of the dial, from the climate entity. */
  @property({ type: Number }) min = 40;

  /** Upper bound of the dial, from the climate entity. */
  @property({ type: Number }) max = 230;

  /** Temperature unit suffix, e.g. `°C`. */
  @property() unit = "°C";

  /** Whether the heater is switched on (hvac mode is heat). */
  @property({ type: Boolean }) active = false;

  /** Whether the device is actively heating right now. */
  @property({ type: Boolean }) heating = false;

  /** Disables the steppers and dims the readout (device disconnected). */
  @property({ type: Boolean }) disabled = false;

  /** Fraction [0, 1] of the ring covered by `value`. */
  private fraction(value: number): number {
    if (this.max <= this.min) {
      return 0;
    }
    return clamp((value - this.min) / (this.max - this.min), 0, 1);
  }

  /** Visual state driving the ring color. */
  private get mode(): "off" | "heating" | "ready" {
    if (!this.active || this.disabled) {
      return "off";
    }
    if (this.current !== undefined && this.target !== undefined) {
      if (this.current >= this.target - 1) {
        return "ready";
      }
    }
    return "heating";
  }

  private emitStep(direction: 1 | -1): void {
    this.dispatchEvent(
      new CustomEvent("dial-step", { detail: { direction }, bubbles: true, composed: true }),
    );
  }

  protected override render() {
    const start = polar(START_ANGLE);
    const end = polar(START_ANGLE + SWEEP);
    const arcPath = `M ${start.x} ${start.y} A ${RADIUS} ${RADIUS} 0 1 1 ${end.x} ${end.y}`;
    const currentFraction = this.current === undefined ? 0 : this.fraction(this.current);
    const marker =
      this.target === undefined || this.disabled
        ? undefined
        : polar(START_ANGLE + SWEEP * this.fraction(this.target));

    return html`
      <div class="dial ${this.mode} ${this.disabled ? "disabled" : ""}">
        <svg viewBox="0 0 200 200" role="img" aria-label="Temperature dial">
          <path class="track" d=${arcPath} pathLength=${PATH_LENGTH} />
          <path
            class="fill"
            d=${arcPath}
            pathLength=${PATH_LENGTH}
            stroke-dasharray="${PATH_LENGTH} ${PATH_LENGTH}"
            stroke-dashoffset=${PATH_LENGTH * (1 - currentFraction)}
          />
          ${marker ? svg`<circle class="marker" cx=${marker.x} cy=${marker.y} r="5" />` : nothing}
        </svg>
        <div class="readout">
          <span class="current"
            >${this.current === undefined || this.disabled ? "—" : Math.round(this.current)}<span
              class="unit"
              >${this.unit}</span
            ></span
          >
          ${
            this.active && !this.disabled && this.target !== undefined
              ? html`<span class="target">➜ ${Math.round(this.target)}${this.unit}</span>`
              : nothing
          }
        </div>
        <button
          class="step minus"
          aria-label="Decrease target temperature"
          ?disabled=${this.disabled}
          @click=${() => this.emitStep(-1)}
        >
          −
        </button>
        <button
          class="step plus"
          aria-label="Increase target temperature"
          ?disabled=${this.disabled}
          @click=${() => this.emitStep(1)}
        >
          +
        </button>
      </div>
    `;
  }

  static override styles = css`
    :host {
      display: block;
      --sb-dial-off: var(--sb-color-off, var(--disabled-text-color, #9e9e9e));
      --sb-dial-heat: var(--sb-color-heating, #ff9800);
      --sb-dial-ready: var(--sb-color-ready, #4caf50);
    }

    .dial {
      position: relative;
      width: min(240px, 100%);
      aspect-ratio: 1;
      margin: 0 auto;
      --dial-color: var(--sb-dial-off);
    }

    .dial.heating {
      --dial-color: var(--sb-dial-heat);
    }

    .dial.ready {
      --dial-color: var(--sb-dial-ready);
    }

    svg {
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
    }

    path {
      fill: none;
      stroke-width: 6;
      stroke-linecap: round;
    }

    .track {
      stroke: var(--divider-color, rgba(127, 127, 127, 0.3));
    }

    .fill {
      stroke: var(--dial-color);
      transition:
        stroke-dashoffset 0.6s ease,
        stroke 0.6s ease;
    }

    .marker {
      fill: var(--dial-color);
      transition: fill 0.6s ease;
    }

    .dial.heating svg {
      animation: sb-breathe 3s ease-in-out infinite;
    }

    @keyframes sb-breathe {
      0%,
      100% {
        filter: drop-shadow(0 0 2px var(--dial-color));
      }
      50% {
        filter: drop-shadow(0 0 10px var(--dial-color));
      }
    }

    @media (prefers-reduced-motion: reduce) {
      .dial.heating svg {
        animation: none;
      }
      .fill,
      .marker {
        transition: none;
      }
    }

    .readout {
      position: absolute;
      inset: 0;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 2px;
      pointer-events: none;
    }

    .current {
      font-size: clamp(2.2rem, 18cqw, 3.2rem);
      font-weight: 300;
      font-variant-numeric: tabular-nums;
      line-height: 1;
      color: var(--primary-text-color);
    }

    .dial.disabled .current {
      color: var(--disabled-text-color, #9e9e9e);
    }

    .unit {
      font-size: 0.4em;
      font-weight: 400;
      color: var(--secondary-text-color);
      vertical-align: super;
    }

    .target {
      font-size: 1rem;
      font-variant-numeric: tabular-nums;
      color: var(--secondary-text-color);
    }

    .step {
      position: absolute;
      bottom: 2%;
      width: 44px;
      height: 44px;
      border: none;
      border-radius: 50%;
      background: var(--secondary-background-color, rgba(127, 127, 127, 0.12));
      color: var(--primary-text-color);
      font-size: 1.4rem;
      line-height: 1;
      cursor: pointer;
      transition:
        transform 0.1s ease,
        background 0.2s ease;
    }

    .step:active {
      transform: scale(0.92);
    }

    .step:disabled {
      cursor: not-allowed;
      opacity: 0.4;
    }

    .minus {
      left: 18%;
    }

    .plus {
      right: 18%;
    }
  `;
}
