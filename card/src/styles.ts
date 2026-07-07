/** Styles for the main card element (the dial styles its own shadow root). */

import { css } from "lit";

export const cardStyles = css`
  :host {
    --sb-heat: var(--sb-color-heating, #ff9800);
    --sb-ready: var(--sb-color-ready, #4caf50);
  }

  ha-card {
    padding: 16px;
  }

  .body {
    display: flex;
    flex-direction: column;
    gap: 14px;
    transition: opacity 0.3s ease;
  }

  .body.disconnected .controls {
    opacity: 0.45;
    pointer-events: none;
  }

  .controls {
    display: flex;
    flex-direction: column;
    gap: 14px;
  }

  /* ---- header ---------------------------------------------------------- */

  .header {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .name {
    flex: 1;
    font-size: 1.1rem;
    font-weight: 500;
    color: var(--primary-text-color);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    flex: none;
  }

  .dot.connected {
    background: var(--sb-ready);
    box-shadow: 0 0 5px var(--sb-ready);
  }

  .dot.disconnected {
    background: var(--error-color, #f44336);
    animation: sb-blink 1.6s ease-in-out infinite;
  }

  @keyframes sb-blink {
    50% {
      opacity: 0.35;
    }
  }

  @media (prefers-reduced-motion: reduce) {
    .dot.disconnected {
      animation: none;
    }
  }

  .battery {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 2px 10px;
    border-radius: 12px;
    background: var(--secondary-background-color, rgba(127, 127, 127, 0.12));
    color: var(--secondary-text-color);
    font-size: 0.85rem;
    font-variant-numeric: tabular-nums;
  }

  /* ---- heat pill ------------------------------------------------------- */

  .heat {
    align-self: center;
    min-width: 60%;
    padding: 12px 24px;
    border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.3));
    border-radius: 28px;
    background: transparent;
    color: var(--primary-text-color);
    font-size: 0.95rem;
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    cursor: pointer;
    transition:
      background 0.25s ease,
      color 0.25s ease,
      box-shadow 0.25s ease,
      transform 0.1s ease;
  }

  .heat:active {
    transform: scale(0.97);
  }

  .heat.on {
    border-color: transparent;
    background: var(--sb-heat);
    color: #fff;
    box-shadow: 0 0 14px color-mix(in srgb, var(--sb-heat) 60%, transparent);
  }

  /* ---- preset chips ---------------------------------------------------- */

  .presets {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 8px;
  }

  .preset {
    padding: 7px 16px;
    border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.3));
    border-radius: 18px;
    background: transparent;
    color: var(--primary-text-color);
    font-size: 0.9rem;
    font-variant-numeric: tabular-nums;
    cursor: pointer;
    animation: sb-fade-in 0.3s ease backwards;
    transition:
      background 0.2s ease,
      color 0.2s ease,
      border-color 0.2s ease,
      transform 0.1s ease;
  }

  .preset:nth-child(2) {
    animation-delay: 0.05s;
  }

  .preset:nth-child(3) {
    animation-delay: 0.1s;
  }

  .preset:nth-child(4) {
    animation-delay: 0.15s;
  }

  .preset:active {
    transform: scale(0.95);
  }

  .preset.active {
    border-color: transparent;
    background: var(--sb-heat);
    color: #fff;
  }

  @keyframes sb-fade-in {
    from {
      opacity: 0;
      transform: translateY(4px);
    }
  }

  @media (prefers-reduced-motion: reduce) {
    .preset {
      animation: none;
    }
  }

  /* ---- pump bar -------------------------------------------------------- */

  .pump {
    position: relative;
    overflow: hidden;
    width: 100%;
    padding: 13px;
    border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.3));
    border-radius: 14px;
    background: transparent;
    color: var(--primary-text-color);
    font-size: 0.95rem;
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    cursor: pointer;
    transition:
      background 0.25s ease,
      color 0.25s ease,
      transform 0.1s ease;
  }

  .pump:active {
    transform: scale(0.98);
  }

  .pump.on {
    border-color: transparent;
    background: var(--primary-color, #03a9f4);
    color: #fff;
  }

  .pump.on::after {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(
      105deg,
      transparent 20%,
      rgba(255, 255, 255, 0.25) 50%,
      transparent 80%
    );
    transform: translateX(-100%);
    animation: sb-airflow 1.8s linear infinite;
  }

  @keyframes sb-airflow {
    to {
      transform: translateX(100%);
    }
  }

  @media (prefers-reduced-motion: reduce) {
    .pump.on::after {
      animation: none;
    }
  }

  /* ---- status + settings ----------------------------------------------- */

  .status {
    display: flex;
    justify-content: center;
    gap: 6px;
    font-size: 0.85rem;
    color: var(--secondary-text-color);
  }

  details {
    border-top: 1px solid var(--divider-color, rgba(127, 127, 127, 0.3));
    padding-top: 4px;
  }

  summary {
    padding: 8px 0;
    font-size: 0.9rem;
    color: var(--secondary-text-color);
    cursor: pointer;
    list-style: none;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  summary::before {
    content: "▸";
    transition: transform 0.2s ease;
  }

  details[open] summary::before {
    transform: rotate(90deg);
  }

  .row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 0;
    font-size: 0.9rem;
    color: var(--primary-text-color);
  }

  .row label {
    flex: 1;
  }

  .row .value {
    min-width: 3.5em;
    text-align: right;
    color: var(--secondary-text-color);
    font-variant-numeric: tabular-nums;
  }

  input[type="range"] {
    flex: 2;
    accent-color: var(--sb-heat);
  }

  input[type="checkbox"] {
    width: 20px;
    height: 20px;
    accent-color: var(--sb-heat);
  }
`;
