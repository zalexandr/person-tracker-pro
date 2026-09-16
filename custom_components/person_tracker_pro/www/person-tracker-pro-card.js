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
    return { rows: 6, columns: 12, min_rows: 4, min_columns: 6, max_columns: 12 };
  }

  static getStubConfig() {
    return { location_entity: "" };
  }

  static getConfigForm() {
    return {
      schema: [
        { name: "location_entity", required: true, selector: { entity: { domain: "device_tracker" } } },
        { name: "confidence_entity", selector: { entity: { domain: "sensor" } } },
        { name: "accuracy_entity", selector: { entity: { domain: "sensor" } } },
        { name: "speed_entity", selector: { entity: { domain: "sensor" } } },
        { name: "sources_entity", selector: { entity: { domain: "sensor" } } },
        { name: "rejected_entity", selector: { entity: { domain: "sensor" } } },
        { name: "moving_entity", selector: { entity: { domain: "binary_sensor" } } },
        { name: "stale_entity", selector: { entity: { domain: "binary_sensor" } } },
        { name: "offline_entity", selector: { entity: { domain: "binary_sensor" } } },
        { name: "show_map", selector: { boolean: {} } },
        { name: "hours_to_show", selector: { number: { min: 1, max: 168, step: 1, mode: "box" } } },
        { name: "map_zoom", selector: { number: { min: 1, max: 20, step: 1, mode: "slider" } } },
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

  _value(entityId, fallback = "—") {
    const state = this._state(entityId);
    if (!state) return fallback;
    return `${state.state}${state.attributes?.unit_of_measurement ? ` ${state.attributes.unit_of_measurement}` : ""}`;
  }

  _binary(entityId) {
    const state = this._state(entityId);
    if (!state) return "—";
    return state.state === "on" ? "Yes" : "No";
  }

  _render() {
    if (!this._hass || !this._config) return;
    const c = this._config;
    const location = this._state(c.location_entity);
    const attrs = location?.attributes || {};
    const lat = attrs.latitude;
    const lon = attrs.longitude;
    const showMap = c.show_map !== false && Number.isFinite(lat) && Number.isFinite(lon);
    const mapHours = Number(c.hours_to_show || 24);
    const zoom = Number(c.map_zoom || 14);
    const rows = [
      ["Confidence", this._value(c.confidence_entity)],
      ["GPS accuracy", this._value(c.accuracy_entity)],
      ["Speed", this._value(c.speed_entity)],
      ["Active sources", this._value(c.sources_entity)],
      ["Rejected samples", this._value(c.rejected_entity)],
      ["Moving", this._binary(c.moving_entity)],
      ["Stale", this._binary(c.stale_entity)],
      ["Offline", this._binary(c.offline_entity)],
    ];

    this.innerHTML = `
      <ha-card>
        <div class="header">
          <ha-icon icon="mdi:map-marker-account"></ha-icon>
          <div class="title">${this._escape(location?.attributes?.friendly_name || "Person Tracker PRO")}</div>
          <div class="state">${this._escape(location?.state || "unknown")}</div>
        </div>
        ${showMap ? `<div class="map"><ha-map .hass="${this._hass}" .config="${JSON.stringify({ entities: [c.location_entity], hours_to_show: mapHours, default_zoom: zoom, auto_fit: true })}"></ha-map></div>` : ""}
        <div class="grid">
          ${rows.filter(([, value]) => value !== "—").map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${this._escape(value)}</div></div>`).join("")}
        </div>
        <div class="footer">
          <span>${this._escape(attrs.zone || location?.state || "Unknown zone")}</span>
          ${attrs.last_update ? `<span>Updated ${this._escape(attrs.last_update)}</span>` : ""}
        </div>
      </ha-card>`;
    this._style();
  }

  _escape(value) {
    return String(value).replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char]));
  }

  _style() {
    if (this.querySelector("style")) return;
    const style = document.createElement("style");
    style.textContent = `
      :host { display:block; }
      ha-card { overflow:hidden; }
      .header { display:flex; align-items:center; gap:10px; padding:16px; }
      .header ha-icon { color:var(--primary-color); }
      .title { font-weight:600; flex:1; }
      .state { color:var(--secondary-text-color); text-transform:capitalize; }
      .map { height:260px; }
      .map ha-map { display:block; width:100%; height:100%; }
      .grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:1px; background:var(--divider-color); }
      .metric { padding:12px; background:var(--card-background-color); }
      .label { font-size:12px; color:var(--secondary-text-color); }
      .value { margin-top:4px; font-size:16px; font-weight:500; }
      .footer { display:flex; justify-content:space-between; gap:12px; padding:12px 16px; color:var(--secondary-text-color); font-size:12px; }
      @media (max-width:600px) { .grid { grid-template-columns:repeat(2,minmax(0,1fr)); } }
    `;
    this.prepend(style);
  }
}

customElements.define("person-tracker-pro-card", PersonTrackerProCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "person-tracker-pro-card",
  name: "Person Tracker PRO",
  description: "Location, confidence, GPS, movement and status in one card.",
  preview: true,
  documentationURL: "https://github.com/zalexandr/person-tracker-pro",
  getEntitySuggestion: (hass, entityId) => {
    if (!entityId || entityId.split(".")[0] !== "device_tracker") return null;
    const state = hass.states[entityId];
    if (!state) return null;
    return { config: { type: "custom:person-tracker-pro-card", location_entity: entityId } };
  },
});
