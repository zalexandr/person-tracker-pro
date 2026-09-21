class PersonTrackerProCard extends HTMLElement {
  setConfig(config) {
    if (!config || !config.location_entity) throw new Error("Select the Person Tracker PRO location entity.");
    this._config = { ...config };
    this._history = null;
    this._historyPromise = null;
    this._render();
    this._loadLocationHistory();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  getCardSize() { return this._config?.compact ? 5 : 12; }
  getGridOptions() { return { rows: 12, columns: 12, min_rows: 5, min_columns: 6, max_columns: 12 }; }

  static getStubConfig() {
    return {
      location_entity: "", sensor_entities: [], binary_sensor_entities: [],
      show_auto_device_sensors: true, show_tracker_details: true, show_attributes: false,
      hide_unavailable: true, show_map: true, hours_to_show: 24, map_zoom: 14,
      show_history: true, show_route: true, show_timeline: true, timeline_items: 12,
      show_statistics: true, show_sensor_history: false, history_hours: 24,
      sensor_columns: 2, compact: false,
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
        { name: "show_route", selector: { boolean: {} } },
        { name: "hours_to_show", selector: { number: { min: 1, max: 168, step: 1, mode: "box" } } },
        { name: "map_zoom", selector: { number: { min: 1, max: 20, step: 1, mode: "slider" } } },
        { name: "show_history", selector: { boolean: {} } },
        { name: "show_statistics", selector: { boolean: {} } },
        { name: "show_timeline", selector: { boolean: {} } },
        { name: "timeline_items", selector: { number: { min: 4, max: 50, step: 1, mode: "box" } } },
        { name: "show_sensor_history", selector: { boolean: {} } },
        { name: "history_hours", selector: { number: { min: 1, max: 168, step: 1, mode: "box" } } },
        { name: "sensor_columns", selector: { number: { min: 1, max: 4, step: 1, mode: "slider" } } },
        { name: "compact", selector: { boolean: {} } },
      ],
      computeLabel: (schema) => ({
        location_entity: "Location entity", sensor_entities: "Additional sensors",
        binary_sensor_entities: "Additional binary sensors", show_auto_device_sensors: "Automatically discover device sensors",
        show_tracker_details: "Show tracker details", show_attributes: "Show sensor attributes",
        hide_unavailable: "Hide unavailable sensors", show_map: "Show map", show_route: "Show route",
        hours_to_show: "Map history (hours)", map_zoom: "Map zoom", show_history: "Show location history",
        show_statistics: "Show statistics", show_timeline: "Show timeline", timeline_items: "Timeline items",
        show_sensor_history: "Show sensor history", history_hours: "Sensor history (hours)", sensor_columns: "Sensor columns",
        compact: "Compact header",
      })[schema.name],
    };
  }

  _state(id) { return id && this._hass ? this._hass.states[id] : undefined; }
  _deviceId(id) { return this._hass?.entities?.[id]?.device_id; }
  _autoEntity(domain, suffix) {
    const location = this._config?.location_entity;
    if (!location) return undefined;
    const prefix = location.replace(/^device_tracker\./, "").replace(/_location$/, "");
    const id = `${domain}.${prefix}_${suffix}`;
    return this._hass?.states[id] ? id : undefined;
  }
  _entity(key, domain, suffix) { return this._config?.[key] || this._autoEntity(domain, suffix); }

  _discoverDeviceEntities() {
    if (!this._hass || this._config?.show_auto_device_sensors === false) return [];
    const location = this._config?.location_entity;
    const deviceId = this._deviceId(location);
    if (deviceId && this._hass.entities) return Object.entries(this._hass.entities).filter(([id, r]) => {
      const d = id.split(".")[0]; return (d === "sensor" || d === "binary_sensor") && r?.device_id === deviceId && this._hass.states[id];
    }).map(([id]) => id);
    const prefix = location?.replace(/^device_tracker\./, "").replace(/_location$/, "");
    return prefix ? Object.keys(this._hass.states).filter((id) => {
      const d = id.split(".")[0]; return (d === "sensor" || d === "binary_sensor") && id.startsWith(`${d}.${prefix}_`);
    }) : [];
  }

  _configuredSensorEntities() {
    const a = Array.isArray(this._config?.sensor_entities) ? this._config.sensor_entities : this._config?.sensor_entities ? [this._config.sensor_entities] : [];
    const b = Array.isArray(this._config?.binary_sensor_entities) ? this._config.binary_sensor_entities : this._config?.binary_sensor_entities ? [this._config.binary_sensor_entities] : [];
    return [...a, ...b].filter((id) => this._state(id));
  }
  _allExtraEntities() {
    return [...new Set([...this._configuredSensorEntities(), ...this._discoverDeviceEntities()])].filter((id) => {
      const d = id.split(".")[0], s = this._state(id); if (d !== "sensor" && d !== "binary_sensor") return false;
      return !this._config?.hide_unavailable || (s?.state !== "unavailable" && s?.state !== "unknown");
    });
  }
  _value(id, fallback = "—") { const s = this._state(id); if (!s) return fallback; const u = s.attributes?.unit_of_measurement; return `${s.state}${u ? ` ${u}` : ""}`; }
  _binary(id) { const s = this._state(id); if (!s) return "—"; return s.state === "on" ? "On" : s.state === "off" ? "Off" : s.state; }
  _friendlyName(id) { return this._state(id)?.attributes?.friendly_name || id; }
  _icon(id) { const s = this._state(id); return s?.attributes?.icon || (id.startsWith("binary_sensor.") ? "mdi:checkbox-marked-circle-outline" : "mdi:chart-line"); }
  _escape(v) { return String(v).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]); }

  _attributes(id) {
    const a = this._state(id)?.attributes; if (!a) return "";
    const ignored = new Set(["friendly_name", "unit_of_measurement", "icon", "device_class", "state_class", "last_reset"]);
    const e = Object.entries(a).filter(([k, v]) => !ignored.has(k) && v != null && typeof v !== "object");
    return e.length ? `<div class="attributes">${e.map(([k, v]) => `<div>${this._escape(k)}: ${this._escape(v)}</div>`).join("")}</div>` : "";
  }

  _trackerDetails(a) {
    if (this._config?.show_tracker_details === false) return "";
    const d = [["Zone", a.zone], ["Movement", a.movement], ["Source", a.source], ["Distance home", a.distance_home], ["Sources", a.source_count], ["Rejected GPS", a.rejected_samples]].filter(([, v]) => v != null && v !== "");
    return d.length ? `<div class="section-title">Tracker details</div><div class="detail-grid">${d.map(([l, v]) => `<div class="detail-item"><div class="label">${this._escape(l)}</div><div class="value">${this._escape(v)}</div></div>`).join("")}</div>` : "";
  }

  _renderExtraSensors() {
    const entities = this._allExtraEntities(); if (!entities.length) return "";
    const columns = Math.min(4, Math.max(1, Number(this._config?.sensor_columns || 2)));
    return `<div class="section-title">Device data</div><div class="sensor-grid" style="--sensor-columns:${columns}">${entities.map((id) => {
      const s = this._state(id), d = id.split(".")[0], v = d === "binary_sensor" ? this._binary(id) : this._value(id), muted = s?.state === "unavailable" || s?.state === "unknown";
      return `<div class="sensor-item${muted ? " muted" : ""}"><ha-icon icon="${this._escape(this._icon(id))}"></ha-icon><div class="sensor-main"><div class="label">${this._escape(this._friendlyName(id))}</div><div class="value">${this._escape(v)}</div>${this._config?.show_attributes ? this._attributes(id) : ""}</div></div>`;
    }).join("")}</div>`;
  }

  async _loadLocationHistory() {
    if (!this._hass || !this._config?.location_entity || this._historyPromise) return;
    const hours = Math.max(1, Math.min(168, Number(this._config?.hours_to_show || 24)));
    this._historyPromise = this._hass.callApi("GET", `history/period?filter_entity_id=${encodeURIComponent(this._config.location_entity)}&minimal_response=false&no_attributes=false&significant_changes_only=false&start_time=${encodeURIComponent(new Date(Date.now() - hours * 3600000).toISOString())}`)
      .then((data) => { this._history = Array.isArray(data) ? data[0] || [] : []; this._render(); })
      .catch(() => { this._history = []; })
      .finally(() => { this._historyPromise = null; });
  }

  _points() {
    return (this._history || []).map((s) => ({
      time: s.last_changed || s.last_updated, state: s.state,
      lat: Number(s.attributes?.latitude), lon: Number(s.attributes?.longitude),
      zone: s.attributes?.zone || s.state,
      movement: s.attributes?.movement,
      speed: Number(s.attributes?.speed_kmh ?? s.attributes?.speed),
    })).filter((p) => Number.isFinite(p.lat) && Number.isFinite(p.lon));
  }

  _distance(a, b) {
    const R = 6371, r = Math.PI / 180, dLat = (b.lat - a.lat) * r, dLon = (b.lon - a.lon) * r;
    const x = Math.sin(dLat / 2) ** 2 + Math.cos(a.lat * r) * Math.cos(b.lat * r) * Math.sin(dLon / 2) ** 2;
    return R * 2 * Math.atan2(Math.sqrt(x), Math.sqrt(1 - x));
  }

  _statistics() {
    const p = this._points(); if (p.length < 1) return "";
    let distance = 0, maxSpeed = 0, movingSeconds = 0;
    for (let i = 1; i < p.length; i++) {
      distance += this._distance(p[i - 1], p[i]);
      if (Number.isFinite(p[i].speed)) maxSpeed = Math.max(maxSpeed, p[i].speed);
      if (p[i].movement === "moving" || p[i].movement === "on") movingSeconds += Math.max(0, (new Date(p[i].time) - new Date(p[i - 1].time)) / 1000);
    }
    const duration = Math.max(0, p.length > 1 ? (new Date(p[p.length - 1].time) - new Date(p[0].time)) / 1000 : 0);
    const fmt = (s) => s >= 3600 ? `${Math.floor(s / 3600)}h ${Math.floor((s % 3600) / 60)}m` : `${Math.floor(s / 60)}m`;
    return `<div class="section-title">Statistics</div><div class="stats-grid"><div class="stat"><div class="label">Distance</div><div class="big">${distance.toFixed(1)} km</div></div><div class="stat"><div class="label">Tracking period</div><div class="big">${fmt(duration)}</div></div><div class="stat"><div class="label">Moving time</div><div class="big">${fmt(movingSeconds)}</div></div><div class="stat"><div class="label">Max speed</div><div class="big">${maxSpeed ? `${maxSpeed.toFixed(0)} km/h` : "—"}</div></div><div class="stat"><div class="label">GPS points</div><div class="big">${p.length}</div></div><div class="stat"><div class="label">Zones / states</div><div class="big">${new Set(p.map((x) => x.zone).filter(Boolean)).size}</div></div></div>`;
  }

  _timeline() {
    const p = this._points(); if (!p.length) return "";
    const items = Number(this._config?.timeline_items || 12);
    const selected = p.slice(-items).reverse();
    return `<div class="section-title">Timeline</div><div class="timeline">${selected.map((x, i) => {
      const dt = x.time ? new Date(x.time) : null, time = dt && !Number.isNaN(dt.valueOf()) ? dt.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "—";
      const detail = [x.zone, x.movement, Number.isFinite(x.speed) ? `${x.speed.toFixed(0)} km/h` : ""].filter(Boolean).join(" · ");
      return `<div class="timeline-item"><div class="dot"></div><div class="timeline-main"><div class="timeline-time">${this._escape(time)}</div><div class="timeline-title">${this._escape(x.zone || x.state || "Location update")}</div><div class="timeline-detail">${this._escape(detail)}</div></div></div>`;
    }).join("")}</div>`;
  }

  async _renderMap(host, config) {
    if (!host || !this._hass) return;
    const element = "hui-map-card";
    if (!customElements.get(element)) await Promise.race([customElements.whenDefined(element), new Promise((r) => setTimeout(r, 1500))]);
    if (!customElements.get(element)) return;
    try { const card = document.createElement(element); card.setConfig(config); card.hass = this._hass; host.replaceChildren(card); } catch (_e) { host.replaceChildren(); }
  }

  async _renderHistory(host, entities) {
    if (!host || !this._hass || !entities.length) return;
    const element = "hui-history-graph-card";
    if (!customElements.get(element)) await Promise.race([customElements.whenDefined(element), new Promise((r) => setTimeout(r, 1500))]);
    if (!customElements.get(element)) return;
    try { const card = document.createElement(element); card.setConfig({ type: "history-graph", entities, hours_to_show: Number(this._config?.history_hours || 24) }); card.hass = this._hass; host.replaceChildren(card); } catch (_e) { host.replaceChildren(); }
  }

  _render() {
    if (!this._hass || !this._config) return;
    const c = this._config, location = this._state(c.location_entity), a = location?.attributes || {};
    const confidence = this._entity("confidence_entity", "sensor", "presence_confidence"), accuracy = this._entity("accuracy_entity", "sensor", "gps_accuracy"), speed = this._entity("speed_entity", "sensor", "speed"), sources = this._entity("sources_entity", "sensor", "active_sources"), rejected = this._entity("rejected_entity", "sensor", "rejected_gps_samples");
    const moving = this._entity("moving_entity", "binary_sensor", "moving"), stale = this._entity("stale_entity", "binary_sensor", "location_stale"), offline = this._entity("offline_entity", "binary_sensor", "location_offline");
    const showMap = c.show_map !== false && Number.isFinite(a.latitude) && Number.isFinite(a.longitude);
    const rows = [["Confidence", this._value(confidence)], ["GPS accuracy", this._value(accuracy)], ["Speed", this._value(speed)], ["Active sources", this._value(sources)], ["Rejected samples", this._value(rejected)], ["Moving", this._binary(moving)], ["Stale", this._binary(stale)], ["Offline", this._binary(offline)]];
    const historyEntities = this._allExtraEntities().filter((id) => id.startsWith("sensor.")).slice(0, 12);
    this.innerHTML = `<ha-card><div class="header${c.compact ? " compact" : ""}"><ha-icon icon="mdi:map-marker-account"></ha-icon><div class="title">${this._escape(location?.attributes?.friendly_name || "Person Tracker PRO")}</div><div class="state">${this._escape(location?.state || "unknown")}</div></div>${showMap ? '<div class="map" id="tracker-map"></div>' : ""}${this._trackerDetails(a)}${c.show_statistics !== false ? this._statistics() : ""}<div class="grid">${rows.filter(([, v]) => v !== "—").map(([l, v]) => `<div class="metric"><div class="label">${this._escape(l)}</div><div class="value">${this._escape(v)}</div></div>`).join("")}</div>${this._renderExtraSensors()}${c.show_timeline !== false ? this._timeline() : ""}${c.show_sensor_history && historyEntities.length ? '<div class="section-title">Sensor history</div><div class="history" id="sensor-history"></div>' : ""}<div class="footer"><span>${this._escape(a.zone || location?.state || "Unknown zone")}</span>${a.last_update ? `<span>Updated ${this._escape(a.last_update)}</span>` : ""}</div></ha-card>`;
    this._style();
    if (showMap) this._renderMap(this.querySelector("#tracker-map"), { type: "map", entities: [c.location_entity], hours_to_show: c.show_history === false ? 0 : Number(c.hours_to_show || 24), default_zoom: Number(c.map_zoom || 14), auto_fit: true });
    if (c.show_sensor_history && historyEntities.length) this._renderHistory(this.querySelector("#sensor-history"), historyEntities);
  }

  _style() {
    if (this.querySelector("style")) return;
    const style = document.createElement("style"); style.textContent = `
      :host { display:block; } ha-card { overflow:hidden; }
      .header { display:flex; align-items:center; gap:10px; padding:16px; } .header.compact { padding:10px 14px; }
      .header ha-icon { color:var(--primary-color); } .title { font-weight:600; flex:1; } .state { color:var(--secondary-text-color); text-transform:capitalize; }
      .map { height:300px; } .map > hui-map-card { display:block; height:100%; }
      .section-title { padding:14px 16px 8px; font-size:13px; font-weight:600; color:var(--secondary-text-color); }
      .grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:1px; background:var(--divider-color); }
      .metric,.detail-item,.stat { padding:12px; background:var(--card-background-color); } .detail-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:1px; background:var(--divider-color); }
      .stats-grid { display:grid; grid-template-columns:repeat(6,minmax(0,1fr)); gap:1px; background:var(--divider-color); }
      .stat .big { margin-top:4px; font-size:18px; font-weight:600; }
      .label { font-size:12px; color:var(--secondary-text-color); } .value { margin-top:4px; font-size:16px; font-weight:500; }
      .sensor-grid { display:grid; grid-template-columns:repeat(var(--sensor-columns),minmax(0,1fr)); gap:1px; background:var(--divider-color); }
      .sensor-item { display:flex; gap:10px; align-items:flex-start; padding:12px; background:var(--card-background-color); min-width:0; }
      .sensor-item ha-icon { color:var(--primary-color); flex:0 0 auto; } .sensor-main { min-width:0; } .sensor-item .value { overflow-wrap:anywhere; }
      .muted { opacity:.6; } .attributes { margin-top:6px; font-size:11px; line-height:1.4; color:var(--secondary-text-color); overflow-wrap:anywhere; }
      .timeline { padding:0 16px 8px; } .timeline-item { display:flex; gap:12px; min-height:58px; position:relative; }
      .timeline-item:not(:last-child)::before { content:""; position:absolute; left:5px; top:12px; bottom:0; width:1px; background:var(--divider-color); }
      .dot { width:11px; height:11px; margin-top:5px; border-radius:50%; background:var(--primary-color); flex:0 0 auto; z-index:1; }
      .timeline-main { padding-bottom:10px; min-width:0; } .timeline-time { font-size:11px; color:var(--secondary-text-color); }
      .timeline-title { font-weight:500; margin-top:2px; } .timeline-detail { font-size:12px; color:var(--secondary-text-color); margin-top:2px; }
      .history { min-height:100px; } .history > hui-history-graph-card { display:block; }
      .footer { display:flex; justify-content:space-between; gap:12px; padding:12px 16px; color:var(--secondary-text-color); font-size:12px; }
      @media(max-width:900px){.stats-grid{grid-template-columns:repeat(3,minmax(0,1fr));}.grid{grid-template-columns:repeat(2,minmax(0,1fr));}}
      @media(max-width:600px){.sensor-grid,.detail-grid{grid-template-columns:repeat(2,minmax(0,1fr));}.stats-grid{grid-template-columns:repeat(2,minmax(0,1fr));}.map{height:240px;}}
      @media(max-width:420px){.grid,.sensor-grid,.detail-grid,.stats-grid{grid-template-columns:1fr;}}
    `; this.prepend(style);
  }
}

if (!customElements.get("person-tracker-pro-card")) customElements.define("person-tracker-pro-card", PersonTrackerProCard);
window.customCards = window.customCards || [];
if (!window.customCards.some((card) => card.type === "person-tracker-pro-card")) {
  window.customCards.push({
    type: "person-tracker-pro-card", name: "Person Tracker PRO",
    description: "Location, extended map, statistics, timeline and device sensors.", preview: true,
    documentationURL: "https://github.com/zalexandr/person-tracker-pro",
    getEntitySuggestion: (hass, entityId) => {
      if (!entityId || entityId.split(".")[0] !== "device_tracker" || !hass.states[entityId]) return null;
      return { config: { type: "custom:person-tracker-pro-card", location_entity: entityId, show_auto_device_sensors: true, show_map: true, show_route: true, hours_to_show: 24, map_zoom: 14, show_history: true, show_statistics: true, show_timeline: true, timeline_items: 12, show_sensor_history: false, history_hours: 24, sensor_columns: 2, hide_unavailable: true, compact: false } };
    },
  });
}
