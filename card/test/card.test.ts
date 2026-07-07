import { beforeEach, describe, expect, test } from "bun:test";
// Side-effect import: defines the custom elements and registers the card.
import "../src/storz-bickel-card";
import type { StorzBickelCard } from "../src/storz-bickel-card";
import type { CardConfig } from "../src/types";
import { CRAFTY_DEVICE, type FakeHass, makeHass, VOLCANO_DEVICE } from "./fixtures";

function config(device: string, overrides: Partial<CardConfig> = {}): CardConfig {
  return { type: "custom:storz-bickel-card", device, ...overrides };
}

async function renderCard(hass: FakeHass, cardConfig: CardConfig): Promise<StorzBickelCard> {
  const card = document.createElement("storz-bickel-card") as StorzBickelCard;
  card.setConfig(cardConfig);
  card.hass = hass;
  document.body.appendChild(card);
  await card.updateComplete;
  return card;
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

beforeEach(() => {
  document.body.innerHTML = "";
});

describe("setConfig", () => {
  test("throws when device is missing", () => {
    const card = document.createElement("storz-bickel-card") as StorzBickelCard;
    expect(() => card.setConfig({ type: "custom:storz-bickel-card", device: "" })).toThrow(
      /device/,
    );
  });
});

describe("capability-driven rendering", () => {
  test("Volcano shows the pump bar and no battery chip", async () => {
    const card = await renderCard(makeHass(), config(VOLCANO_DEVICE));
    expect(card.shadowRoot?.querySelector(".pump")).not.toBeNull();
    expect(card.shadowRoot?.querySelector(".battery")).toBeNull();
  });

  test("Crafty shows the battery chip and no pump bar", async () => {
    const card = await renderCard(makeHass(), config(CRAFTY_DEVICE));
    expect(card.shadowRoot?.querySelector(".pump")).toBeNull();
    expect(card.shadowRoot?.querySelector(".battery")?.textContent).toContain("87%");
  });

  test("device name prefers the user-assigned name, config name wins overall", async () => {
    const crafty = await renderCard(makeHass(), config(CRAFTY_DEVICE));
    expect(crafty.shadowRoot?.querySelector(".name")?.textContent).toBe("My Crafty");

    document.body.innerHTML = "";
    const named = await renderCard(makeHass(), config(CRAFTY_DEVICE, { name: "Bedside" }));
    expect(named.shadowRoot?.querySelector(".name")?.textContent).toBe("Bedside");
  });

  test("disconnected device dims controls and flips the header dot", async () => {
    const hass = makeHass();
    const connection = hass.states["binary_sensor.volcano_connection"];
    if (connection) {
      connection.state = "off";
    }
    const card = await renderCard(hass, config(VOLCANO_DEVICE));
    expect(card.shadowRoot?.querySelector(".body")?.classList.contains("disconnected")).toBe(true);
    expect(card.shadowRoot?.querySelector(".dot.disconnected")).not.toBeNull();
  });
});

describe("presets", () => {
  test("chip matching the target is active; tapping one calls set_temperature", async () => {
    const hass = makeHass();
    const card = await renderCard(hass, config(VOLCANO_DEVICE, { presets: [175, 185, 195] }));
    const chips = [...(card.shadowRoot?.querySelectorAll(".preset") ?? [])];
    expect(chips).toHaveLength(3);
    // Target is 195 in the fixture.
    expect(chips[2]?.classList.contains("active")).toBe(true);

    (chips[0] as HTMLButtonElement).click();
    expect(hass.serviceCalls).toEqual([
      {
        domain: "climate",
        service: "set_temperature",
        data: { entity_id: "climate.renamed_by_user", temperature: 175 },
      },
    ]);
  });
});

describe("heat and pump controls", () => {
  test("heat pill toggles hvac mode off when heating", async () => {
    const hass = makeHass();
    const card = await renderCard(hass, config(VOLCANO_DEVICE));
    (card.shadowRoot?.querySelector(".heat") as HTMLButtonElement).click();
    expect(hass.serviceCalls).toEqual([
      {
        domain: "climate",
        service: "set_hvac_mode",
        data: { entity_id: "climate.renamed_by_user", hvac_mode: "off" },
      },
    ]);
  });

  test("pump bar turns the pump switch on", async () => {
    const hass = makeHass();
    const card = await renderCard(hass, config(VOLCANO_DEVICE));
    (card.shadowRoot?.querySelector(".pump") as HTMLButtonElement).click();
    expect(hass.serviceCalls).toEqual([
      {
        domain: "switch",
        service: "turn_on",
        data: { entity_id: "switch.volcano_pump" },
      },
    ]);
  });
});

describe("dial steppers", () => {
  test("rapid taps debounce into a single set_temperature call", async () => {
    const hass = makeHass();
    const card = await renderCard(hass, config(VOLCANO_DEVICE));
    card.debounceMs = 20;
    const dial = card.shadowRoot?.querySelector("sb-temp-dial");
    const step = (direction: number) =>
      dial?.dispatchEvent(
        new CustomEvent("dial-step", { detail: { direction }, bubbles: true, composed: true }),
      );

    step(1);
    step(1);
    step(1);
    expect(hass.serviceCalls).toHaveLength(0);

    await sleep(60);
    // Fixture target is 195; three +1 steps land on 198.
    expect(hass.serviceCalls).toEqual([
      {
        domain: "climate",
        service: "set_temperature",
        data: { entity_id: "climate.renamed_by_user", temperature: 198 },
      },
    ]);
  });

  test("steps clamp to the climate entity's max", async () => {
    const hass = makeHass();
    const climate = hass.states["climate.renamed_by_user"];
    if (climate) {
      climate.attributes.temperature = 230;
    }
    const card = await renderCard(hass, config(VOLCANO_DEVICE));
    card.debounceMs = 20;
    card.shadowRoot
      ?.querySelector("sb-temp-dial")
      ?.dispatchEvent(
        new CustomEvent("dial-step", { detail: { direction: 1 }, bubbles: true, composed: true }),
      );
    await sleep(60);
    expect(hass.serviceCalls[0]?.data.temperature).toBe(230);
  });
});

describe("settings", () => {
  test("LED brightness slider change calls number.set_value", async () => {
    const hass = makeHass();
    const card = await renderCard(hass, config(VOLCANO_DEVICE));
    const slider = card.shadowRoot?.querySelector(
      "#number-volcano_led_brightness",
    ) as HTMLInputElement;
    expect(slider).not.toBeNull();
    slider.value = "40";
    slider.dispatchEvent(new Event("change"));
    expect(hass.serviceCalls).toEqual([
      {
        domain: "number",
        service: "set_value",
        data: { entity_id: "number.volcano_led_brightness", value: 40 },
      },
    ]);
  });

  test("vibration toggle flips the switch", async () => {
    const hass = makeHass();
    const card = await renderCard(hass, config(CRAFTY_DEVICE));
    const toggle = card.shadowRoot?.querySelector("#vibration") as HTMLInputElement;
    toggle.dispatchEvent(new Event("change"));
    expect(hass.serviceCalls).toEqual([
      {
        domain: "switch",
        service: "turn_off",
        data: { entity_id: "switch.crafty_vibration" },
      },
    ]);
  });
});

describe("card metadata", () => {
  test("registers in window.customCards once", () => {
    const entries = (window.customCards ?? []).filter((card) => card.type === "storz-bickel-card");
    expect(entries).toHaveLength(1);
  });

  test("getCardSize and getGridOptions report sizing", async () => {
    const card = await renderCard(makeHass(), config(VOLCANO_DEVICE));
    expect(card.getCardSize()).toBeGreaterThan(0);
    expect(card.getGridOptions().min_columns).toBeGreaterThan(0);
  });
});
