class PersonTrackerProCard extends HTMLElement {
  setConfig(config) {
    if (!config || !config.location_entity) throw new Error("Select the Person Tracker PRO location entity.");
    this._config = { ...config };
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  getCardSize() {
    return this._config?.compact ? 4 : 8;
  }

  getGridOptions() {
    return { rows: 8, columns: 12, min_rows: 4, min_columns: 6, max_columns: 12 };
  }

  static getStubConfig() {
    return {
      location_entity: "",
      sensor_entities: [],
      binary_sensor_entities: [],
      show_auto_device_sensors: true,
      show_tracker_details: true,
      show_attributes: false,
      hide_unavailable: true,
      show_map: true,
      hours_to_show: 24,
      map_zoom: 14,
      show_history: true,
      show_sensor_history: false,
      history_hours: 24,
      sensor_columns: 2,
      compact: false,
    };
  }

  static getConfigForm() {
    return {
      schema: [
        { name: "location_entity", required: true, selector: { entity: { domain: "device_tracker" } } },
        { name: "sensor_entities", selector: { entity: { domain: "sensor", multiple: true } } },
        { name: "binary_sensor_entities", selector: { entity: { domain: "binary_sensor", multiple: true } } },
        { name: "show_auto_device_sensors", selector: { boolean: {} } },
        { name: "show_tracker_details", selector: { boolean: {} } },
        { name: "show_attributes", selector: { boolean: {} } },
        { name: "hide_unavailable", selector: { boolean: {} } },
        { name: "show_map", selector: { boolean: {} } },
        { name: "hours_to_show", selector: { number: { min: 1, max: 168, step: 1, mode: "box" } } },
        { name: "map_zoom", selector: { number: { min: 1, max: 20, step: 1, mode: "slider" } } },
        { name: "show_history", selector: { boolean: {} } },
        { name: "show_sensor_history", selector: { boolean: {} } },
        { name: "history_hours", selector: { number: { min: 1, max: 168, step: 1, mode: "box" } } },
        { name: "sensor_columns", selector: { number: { min: 1, max: 4, step: 1, mode: "slider" } } },
        { name: "compact", selector: { boolean: {} } },
      ],
      computeLabel: (schema) => ({
        location_entity: "Location entity",
        sensor_entities: "Additional sensors",
        binary_sensor_entities: "Additional binary sensors",
        show_auto_device_sensors: "Automatically discover device sensors",
        show_tracker_details: "Show tracker details",
        show_attributes: "Show sensor attributes",
        hide_unavailable: "Hide unavailable sensors",
        show_map: "Show map",
        hours_to_show: "Map history (hours)",
        map_zoom: "Map zoom",
        show_history: "Show location history",
        show_sensor_history: "Show sensor history",
        history_hours: "Sensor history (hours)",
        sensor_columns: "Sensor columns",
        compact: "Compact header",
      })[schema.name],
    };
  }

  _state(entityId) {
    return entityId && this._hass ? this._hass.states[entityId] : undefined;
  }

  _deviceId(entityId) {
    return this._hass?.entities?.[entityId]?.device_id;
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

  _discoverDeviceEntities() {
    if (!this._hass || this._config?.show_auto_device_sensors === false) return [];
    const location = this._config?.location_entity;
    const deviceId = this._deviceId(location);
    if (deviceId && this._hass.entities) {
      return Object.entries(this._hass.entities)
        .filter(([entityId, registry]) => {
          const domain = entityId.split(".")[0];
          return (domain === "sensor" || domain === "binary_sensor") && registry?.device_id === deviceId && this._hass.states[entityId];
        })
        .map(([entityId]) => entityId);
    }
    const prefix = location?.replace(/^device_tracker\./, "").replace(/_location$/, "");
    if (!prefix) return [];
    return Object.keys(this._hass.states).filter((entityId) => {
      const domain = entityId.split(".")[0];
      return (domain === "sensor" || domain === "binary_sensor") && entityId.startsWith(`${domain}.${prefix}_`);
    });
  }

  _configuredSensorEntities() {
    const configured = [
      ...(Array.isArray(this._config?.sensor_entities) ? this._config.sensor_entities : this._config?.sensor_entities ? [this._config.sensor_entities] : []),
      ...(Array.isArray(this._config?.binary_sensor_entities) ? this._config.binary_sensor_entities : this._config?.binary_sensor_entities ? [this._config.binary_sensor_entities] : []),
    ];
    return configured.filter((entityId) => this._state(entityId));
  }

  _allExtraEntities() {
    return [...new Set([...this._configuredSensorEntities(), ...this._discoverDeviceEntities()])].filter((entityId) => {
      const domain = entityId.split(".")[0];
      const state = this._state(entityId);
      if (domain !== "sensor" && domain !== "binary_sensor") return false;
      return !this._config?.hide_unavailable || (state?.state !== "unavailable" && state?.state !== "unknown");
    });
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
    if (state.state === "on") return "On";
    if (state.state === "off") return "Off";
    return state.state;
  }

  _friendlyName(entityId) {
    return this._state(entityId)?.attributes?.friendly_name || entityId;
  }

  _icon(entityId) {
    const state = this._state(entityId);
    if (state?.attributes?.icon) return state.attributes.icon;
    return entityId.startsWith("binary_sensor.") ? "mdi:checkbox-marked-circle-outline" : "mdi:chart-line";
  }

  _attributes(entityId) {
    const attributes = this._state(entityId)?.attributes;
    if (!attributes) return "";
    const ignored = new Set(["friendly_name", "unit_of_measurement", "icon", "device_class", "state_class", "last_reset"]);
    const entries = Object.entries(attributes).filter(([key, value]) => !ignored.has(key) && value !== undefined && value !== null && typeof value !== "object");
    if (!entries.length) return "";
    return `<div class="attributes">${entries.map(([key, value]) => `<div>${this._escape(key)}: ${this._escape(value)}</div>`).join("")}</div>`;
  }

  _trackerDetails(attrs) {
    if (this._config?.show_tracker_details === false) return "";
    const details = [
      ["Zone", attrs.zone],
      ["Movement", attrs.movement],
      ["Source", attrs.source],
      ["Distance home", attrs.distance_home],
      ["Sources", attrs.source_count],
      ["Rejected GPS", attrs.rejected_samples],
    ].filter(([, value]) => value !== undefined && value !== null && value !== "");
    if (!details.length) return "";
    return `<div class="section-title">Tracker details</div><div class="detail-grid">${details.map(([label, value]) => `<div class="detail-item"><div class="label">${this._escape(label)}</div><div class="value">${this._escape(value)}</div></div>`).join("")}</div>`;
  }

  _renderExtraSensors() {
    const entities = this._allExtraEntities();
    if (!entities.length) return "";
    const columns = Math.min(4, Math.max(1, Number(this._config?.sensor_columns || 2)));
    const showAttributes = this._config?.show_attributes === true;
    return `<div class="section-title">Device data</div><div class="sensor-grid" style="--sensor-columns:${columns}">${entities.map((entityId) => {
      const state = this._state(entityId);
      const domain = entityId.split(".")[0];
      const value = domain === "binary_sensor" ? this._binary(entityId) : this._value(entityId);
      const muted = state?.state === "unavailable" || state?.state === "unknown";
      return `<div class="sensor-item${muted ? " muted" : ""}"><ha-icon icon="${this._escape(this._icon(entityId))}"></ha-icon><div class="sensor-main"><div class="label">${this._escape(this._friendlyName(entityId))}</div><div class="value">${this._escape(value)}</div>${showAttributes ? this._attributes(entityId) : ""}</div></div>`;
    }).join("")}</div>`;
  }

  async _renderMap(host, config) {
    if (!host || !this._hass) return;
    const element = "hui-map-card";
    if (!customElements.get(element)) await Promise.race([customElements.whenDefined(element), new Promise((resolve) => setTimeout(resolve, 1500))]);
    if (!customElements.get(element)) return;
    try {
      const card = document.createElement(element);
      card.setConfig(config);
      card.hass = this._hass;
      host.replaceChildren(card);
    } catch (_error) { host.replaceChildren(); }
  }

  async _renderHistory(host, entities) {
    if (!host || !this._hass || !entities.length) return;
    const element = "hui-history-graph-card";
    if (!customElements.get(element)) await Promise.race([customElements.whenDefined(element), new Promise((resolve) => setTimeout(resolve, 1500))]);
    if (!customElements.get(element)) return;
    try {
      const card = document.createElement(element);
      card.setConfig({ type: "history-graph", entities, hours_to_show: Number(this._config?.history_hours || 24) });
      card.hass = this._hass;
      host.replaceChildren(card);
    } catch (_error) { host.replaceChildren(); }
  }

  _render() {
    if (!this._hass || !this._config) return;
    const c = this._config;
    const location = this._state(c.location_entity);
    const attrs = location?.attributes || {};
    const confidence = this._entity("confidence_entity", "sensor", "presence_confidence");
    const accuracy = this._entity("accuracy_entity", "sensor", "gps_accuracy");
    const speed = this._entity("speed_entity", "sensor", "speed");
    const sources = this._entity("sources_entity", "sensor", "active_sources");
    const rejected = this._entity("rejected_entity", "sensor", "rejected_gps_samples");
    const moving = this._entity("moving_entity", "binary_sensor", "moving");
    const stale = this._entity("stale_entity", "binary_sensor", "location_stale");
    const offline = this._entity("offline_entity", "binary_sensor", "location_offline");
    const showMap = c.show_map !== false && Number.isFinite(attrs.latitude) && Number.isFinite(attrs.longitude);
    const rows = [["Confidence", this._value(confidence)], ["GPS accuracy", this._value(accuracy)], ["Speed", this._value(speed)], ["Active sources", this._value(sources)], ["Rejected samples", this._value(rejected)], ["Moving", this._binary(moving)], ["Stale", this._binary(stale)], ["Offline", this._binary(offline)]];
    const historyEntities = this._allExtraEntities().filter((entityId) => entityId.startsWith("sensor.")).slice(0, 12);

    this.innerHTML = `<ha-card><div class="header${c.compact ? " compact" : ""}"><ha-icon icon="mdi:map-marker-account"></ha-icon><div class="title">${this._escape(location?.attributes?.friendly_name || "Person Tracker PRO")}</div><div class="state">${this._escape(location?.state || "unknown")}</div></div>${showMap ? '<div class="map" id="tracker-map"></div>' : ""}${this._trackerDetails(attrs)}<div class="grid">${rows.filter(([, value]) => value !== "—").map(([label, value]) => `<div class="metric"><div class="label">${this._escape(label)}</div><div class="value">${this._escape(value)}</div></div>`).join("")}</div>${this._renderExtraSensors()}${c.show_sensor_history && historyEntities.length ? '<div class="section-title">Sensor history</div><div class="history" id="sensor-history"></div>' : ""}<div class="footer"><span>${this._escape(attrs.zone || location?.state || "Unknown zone")}</span>${attrs.last_update ? `<span>Updated ${this._escape(attrs.last_update)}</span>` : ""}</div></ha-card>`;

    this._style();
    if (showMap) this._renderMap(this.querySelector("#tracker-map"), { type: "map", entities: [c.location_entity], hours_to_show: c.show_history === false ? 0 : Number(c.hours_to_show || 24), default_zoom: Number(c.map_zoom || 14), auto_fit: true });
    if (c.show_sensor_history && historyEntities.length) this._renderHistory(this.querySelector("#sensor-history"), historyEntities);
  }

  _escape(value) {
    return String(value).replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]);
  }

  _style() {
    if (this.querySelector("style")) return;
    const style = document.createElement("style");
    style.textContent = `
      :host { display: block; }
      ha-card { overflow: hidden; }
      .header { display: flex; align-items: center; gap: 10px; padding: 16px; }
      .header.compact { padding: 10px 14px; }
      .header ha-icon { color: var(--primary-color); }
      .title { font-weight: 600; flex: 1; }
      .state { color: var(--secondary-text-color); text-transform: capitalize; }
      .map { height: 260px; }
      .map > hui-map-card { display: block; height: 100%; }
      .section-title { padding: 14px 16px 8px; font-size: 13px; font-weight: 600; color: var(--secondary-text-color); }
      .grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 1px; background: var(--divider-color); }
      .metric, .detail-item { padding: 12px; background: var(--card-background-color); }
      .detail-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1px; background: var(--divider-color); }
      .label { font-size: 12px; color: var(--secondary-text-color); }
      .value { margin-top: 4px; font-size: 16px; font-weight: 500; }
      .sensor-grid { display: grid; grid-template-columns: repeat(var(--sensor-columns), minmax(0, 1fr)); gap: 1px; background: var(--divider-color); }
      .sensor-item { display: flex; gap: 10px; align-items: flex-start; padding: 12px; background: var(--card-background-color); min-width: 0; }
      .sensor-item ha-icon { color: var(--primary-color); flex: 0 0 auto; }
      .sensor-main { min-width: 0; }
      .sensor-item .value { overflow-wrap: anywhere; }
      .muted { opacity: 0.6; }
      .attributes { margin-top: 6px; font-size: 11px; line-height: 1.4; color: var(--secondary-text-color); overflow-wrap: anywhere; }
      .history { min-height: 100px; }
      .history > hui-history-graph-card { display: block; }
      .footer { display: flex; justify-content: space-between; gap: 12px; padding: 12px 16px; color: var(--secondary-text-color); font-size: 12px; }
      @media (max-width: 700px) { .grid, .sensor-grid, .detail-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
      @media (max-width: 420px) { .grid, .sensor-grid, .detail-grid { grid-template-columns: 1fr; } }
    `;
    this.prepend(style);
  }
}

if (!customElements.get("person-tracker-pro-card")) customElements.define("person-tracker-pro-card", PersonTrackerProCard);

window.customCards = window.customCards || [];
if (!window.customCards.some((card) => card.type === "person-tracker-pro-card")) {
  window.customCards.push({
    type: "person-tracker-pro-card",
    name: "Person Tracker PRO",
    description: "Rich location, tracker and selectable device sensor dashboard.",
    preview: true,
    documentationURL: "https://github.com/zalexandr/person-tracker-pro",
    getEntitySuggestion: (hass, entityId) => {
      if (!entityId || entityId.split(".")[0] !== "device_tracker" || !hass.states[entityId]) return null;
      return { config: { type: "custom:person-tracker-pro-card", location_entity: entityId, show_auto_device_sensors: true, show_tracker_details: true, show_map: true, hours_to_show: 24, map_zoom: 14, show_history: true, show_sensor_history: false, history_hours: 24, sensor_columns: 2, hide_unavailable: true, compact: false } };
    },
  });
}
