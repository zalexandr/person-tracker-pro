class PersonTrackerProCard extends HTMLElement {
  setConfig(config) {
    if (!config || !config.location_entity) {
      throw new Error("Select the Person Tracker PRO location entity.");
    }
    this._config = { ...config };
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  getCardSize() {
    return 6;
  }

  getGridOptions() {
    return {
      rows: 6,
      columns: 12,
      min_rows: 4,
      min_columns: 6,
      max_columns: 12,
    };
  }

  static getStubConfig() {
    return {
      location_entity: "",
      show_map: true,
      hours_to_show: 24,
      map_zoom: 14,
      show_history: true,
    };
  }

  static getConfigForm() {
    return {
      schema: [
        {
          name: "location_entity",
          required: true,
          selector: { entity: { domain: "device_tracker" } },
        },
        {
          name: "confidence_entity",
          selector: { entity: { domain: "sensor" } },
        },
        {
          name: "accuracy_entity",
          selector: { entity: { domain: "sensor" } },
        },
        {
          name: "speed_entity",
          selector: { entity: { domain: "sensor" } },
        },
        {
          name: "sources_entity",
          selector: { entity: { domain: "sensor" } },
        },
        {
          name: "rejected_entity",
          selector: { entity: { domain: "sensor" } },
        },
        {
          name: "moving_entity",
          selector: { entity: { domain: "binary_sensor" } },
        },
        {
          name: "stale_entity",
          selector: { entity: { domain: "binary_sensor" } },
        },
        {
          name: "offline_entity",
          selector: { entity: { domain: "binary_sensor" } },
        },
        { name: "show_map", selector: { boolean: {} } },
        {
          name: "hours_to_show",
          selector: {
            number: { min: 1, max: 168, step: 1, mode: "box" },
          },
        },
        {
          name: "map_zoom",
          selector: {
            number: { min: 1, max: 20, step: 1, mode: "slider" },
          },
        },
        { name: "show_history", selector: { boolean: {} } },
      ],
      computeLabel: (schema) => ({
        location_entity: "Location entity",
        confidence_entity: "Presence confidence",
        accuracy_entity: "GPS accuracy",
        speed_entity: "Speed",
        sources_entity: "Active sources",
        rejected_entity: "Rejected GPS samples",
        moving_entity: "Moving",
        stale_entity: "Location stale",
        offline_entity: "Location offline",
        show_map: "Show map",
        hours_to_show: "Map history (hours)",
        map_zoom: "Map zoom",
        show_history: "Show history",
      })[schema.name],
    };
  }

  _state(entityId) {
    return entityId && this._hass ? this._hass.states[entityId] : undefined;
  }

  _autoEntity(domain, suffix) {
    const location = this._config?.location_entity;
    if (!location) return undefined;
    const prefix = location.replace(/^device_tracker\./, "").replace(/_location$/, "");
    const entityId = `${domain}.${prefix}_${suffix}`;
    return this._hass?.states[entityId] ? entityId : undefined;
  }

  _entity(configKey, domain, suffix) {
    return this._config?.[configKey] || this._autoEntity(domain, suffix);
  }

  _value(entityId, fallback = "—") {
    const state = this._state(entityId);
    if (!state) return fallback;
    const unit = state.attributes?.unit_of_measurement;
    return `${state.state}${unit ? ` ${unit}` : ""}`;
  }

  _binary(entityId) {
    const state = this._state(entityId);
    if (!state) return "—";
    return state.state === "on" ? "Yes" : "No";
  }

  async _renderMap(host, config) {
    if (!host || !this._hass) return;
    const mapElement = "hui-map-card";
    if (!customElements.get(mapElement)) {
      await Promise.race([
        customElements.whenDefined(mapElement),
        new Promise((resolve) => setTimeout(resolve, 1500)),
      ]);
    }
    if (!customElements.get(mapElement)) {
      host.replaceChildren();
      return;
    }
    try {
      const map = document.createElement(mapElement);
      map.setConfig(config);
      map.hass = this._hass;
      host.replaceChildren(map);
    } catch (_error) {
      host.replaceChildren();
    }
  }

  _render() {
    if (!this._hass || !this._config) return;

    const c = this._config;
    const location = this._state(c.location_entity);
    const attrs = location?.attributes || {};
    const confidence = this._entity(
      "confidence_entity",
      "sensor",
      "presence_confidence",
    );
    const accuracy = this._entity("accuracy_entity", "sensor", "gps_accuracy");
    const speed = this._entity("speed_entity", "sensor", "speed");
    const sources = this._entity("sources_entity", "sensor", "active_sources");
    const rejected = this._entity(
      "rejected_entity",
      "sensor",
      "rejected_gps_samples",
    );
    const moving = this._entity("moving_entity", "binary_sensor", "moving");
    const stale = this._entity("stale_entity", "binary_sensor", "location_stale");
    const offline = this._entity(
      "offline_entity",
      "binary_sensor",
      "location_offline",
    );

    const showMap =
      c.show_map !== false &&
      Number.isFinite(attrs.latitude) &&
      Number.isFinite(attrs.longitude);

    const rows = [
      ["Confidence", this._value(confidence)],
      ["GPS accuracy", this._value(accuracy)],
      ["Speed", this._value(speed)],
      ["Active sources", this._value(sources)],
      ["Rejected samples", this._value(rejected)],
      ["Moving", this._binary(moving)],
      ["Stale", this._binary(stale)],
      ["Offline", this._binary(offline)],
    ];

    this.innerHTML = `
      <ha-card>
        <div class="header">
          <ha-icon icon="mdi:map-marker-account"></ha-icon>
          <div class="title">${this._escape(
            location?.attributes?.friendly_name || "Person Tracker PRO",
          )}</div>
          <div class="state">${this._escape(location?.state || "unknown")}</div>
        </div>
        ${showMap ? '<div class="map" id="tracker-map"></div>' : ""}
        <div class="grid">
          ${rows
            .filter(([, value]) => value !== "—")
            .map(
              ([label, value]) =>
                `<div class="metric"><div class="label">${label}</div><div class="value">${this._escape(value)}</div></div>`,
            )
            .join("")}
        </div>
        <div class="footer">
          <span>${this._escape(attrs.zone || location?.state || "Unknown zone")}</span>
          ${attrs.last_update ? `<span>Updated ${this._escape(attrs.last_update)}</span>` : ""}
        </div>
      </ha-card>`;

    this._style();
    if (showMap) {
      this._renderMap(this.querySelector("#tracker-map"), {
        type: "map",
        entities: [c.location_entity],
        hours_to_show: c.show_history === false ? 0 : Number(c.hours_to_show || 24),
        default_zoom: Number(c.map_zoom || 14),
        auto_fit: true,
      });
    }
  }

  _escape(value) {
    return String(value).replace(/[&<>"']/g, (char) =>
      ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
      })[char],
    );
  }

  _style() {
    if (this.querySelector("style")) return;
    const style = document.createElement("style");
    style.textContent = `
      :host { display: block; }
      ha-card { overflow: hidden; }
      .header { display: flex; align-items: center; gap: 10px; padding: 16px; }
      .header ha-icon { color: var(--primary-color); }
      .title { font-weight: 600; flex: 1; }
      .state { color: var(--secondary-text-color); text-transform: capitalize; }
      .map { height: 260px; }
      .map > hui-map-card { display: block; height: 100%; }
      .grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 1px; background: var(--divider-color); }
      .metric { padding: 12px; background: var(--card-background-color); }
      .label { font-size: 12px; color: var(--secondary-text-color); }
      .value { margin-top: 4px; font-size: 16px; font-weight: 500; }
      .footer { display: flex; justify-content: space-between; gap: 12px; padding: 12px 16px; color: var(--secondary-text-color); font-size: 12px; }
      @media (max-width: 600px) { .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
    `;
    this.prepend(style);
  }
}

if (!customElements.get("person-tracker-pro-card")) {
  customElements.define("person-tracker-pro-card", PersonTrackerProCard);
}

window.customCards = window.customCards || [];
if (!window.customCards.some((card) => card.type === "person-tracker-pro-card")) {
  window.customCards.push({
    type: "person-tracker-pro-card",
    name: "Person Tracker PRO",
    description: "Location, confidence, GPS, movement and status in one card.",
    preview: true,
    documentationURL: "https://github.com/zalexandr/person-tracker-pro",
    getEntitySuggestion: (hass, entityId) => {
      if (
        !entityId ||
        entityId.split(".")[0] !== "device_tracker" ||
        !hass.states[entityId]
      ) {
        return null;
      }
      return {
        config: {
          type: "custom:person-tracker-pro-card",
          location_entity: entityId,
          show_map: true,
          hours_to_show: 24,
          map_zoom: 14,
          show_history: true,
        },
      };
    },
  });
}
