const PT_I18N = {
  en: {tracker:"Tracker",details:"Tracker details",data:"Device data",map:"Map",route:"Route",statistics:"Statistics",timeline:"Timeline",sensorHistory:"Sensor history",zone:"Zone",movement:"Movement",source:"Source",distanceHome:"Distance home",sources:"Sources",rejectedGps:"Rejected GPS",confidence:"Confidence",gpsAccuracy:"GPS accuracy",speed:"Speed",activeSources:"Active sources",rejectedSamples:"Rejected samples",moving:"Moving",stale:"Stale",offline:"Offline",distance:"Distance",trackingPeriod:"Tracking period",movingTime:"Moving time",maxSpeed:"Max speed",gpsPoints:"GPS points",zones:"Zones / states",noLocation:"No GPS history",on:"On",off:"Off",home:"Home",unknown:"Unknown",now:"Now"},
  pl: {tracker:"Tracker",details:"Szczegóły trackera",data:"Dane urządzenia",map:"Mapa",route:"Trasa",statistics:"Statystyki",timeline:"Oś czasu",sensorHistory:"Historia sensorów",zone:"Strefa",movement:"Ruch",source:"Źródło",distanceHome:"Odległość od domu",sources:"Źródła",rejectedGps:"Odrzucony GPS",confidence:"Pewność",gpsAccuracy:"Dokładność GPS",speed:"Prędkość",activeSources:"Aktywne źródła",rejectedSamples:"Odrzucone próbki",moving:"Ruch",stale:"Nieaktualne",offline:"Offline",distance:"Dystans",trackingPeriod:"Okres śledzenia",movingTime:"Czas ruchu",maxSpeed:"Maks. prędkość",gpsPoints:"Punkty GPS",zones:"Strefy / stany",noLocation:"Brak historii GPS",on:"Włączony",off:"Wyłączony",home:"Dom",unknown:"Nieznany",now:"Teraz"},
  ru: {tracker:"Трекер",details:"Данные трекера",data:"Данные устройства",map:"Карта",route:"Маршрут",statistics:"Статистика",timeline:"Хронология",sensorHistory:"История сенсоров",zone:"Зона",movement:"Движение",source:"Источник",distanceHome:"Расстояние до дома",sources:"Источники",rejectedGps:"Отклонённый GPS",confidence:"Уверенность",gpsAccuracy:"Точность GPS",speed:"Скорость",activeSources:"Активные источники",rejectedSamples:"Отклонённые точки",moving:"Движение",stale:"Устарел",offline:"Офлайн",distance:"Расстояние",trackingPeriod:"Период отслеживания",movingTime:"Время движения",maxSpeed:"Макс. скорость",gpsPoints:"GPS-точки",zones:"Зоны / состояния",noLocation:"Нет истории GPS",on:"Вкл",off:"Выкл",home:"Дом",unknown:"Неизвестно",now:"Сейчас"},
  uk: {tracker:"Трекер",details:"Дані трекера",data:"Дані пристрою",map:"Мапа",route:"Маршрут",statistics:"Статистика",timeline:"Хронологія",sensorHistory:"Історія сенсорів",zone:"Зона",movement:"Рух",source:"Джерело",distanceHome:"Відстань до дому",sources:"Джерела",rejectedGps:"Відхилений GPS",confidence:"Впевненість",gpsAccuracy:"Точність GPS",speed:"Швидкість",activeSources:"Активні джерела",rejectedSamples:"Відхилені точки",moving:"Рух",stale:"Застарілий",offline:"Офлайн",distance:"Відстань",trackingPeriod:"Період відстеження",movingTime:"Час руху",maxSpeed:"Макс. швидкість",gpsPoints:"GPS-точки",zones:"Зони / стани",noLocation:"Немає історії GPS",on:"Увімк",off:"Вимк",home:"Дім",unknown:"Невідомо",now:"Зараз"}
};

class PersonTrackerProCard extends HTMLElement {
  setConfig(config) {
    if (!config || !config.location_entity) throw new Error("Select the Person Tracker PRO location entity.");
    this._config = { ...config };
    this._history = null;
    this._historyPromise = null;
    this._renderedMap = false;
    this._render();
    this._loadLocationHistory();
  }

  set hass(hass) { this._hass = hass; this._render(); }
  getCardSize() { return this._config?.compact ? 7 : 14; }
  getGridOptions() { return { rows: 12, columns: 12, min_rows: 5, min_columns: 6, max_columns: 12 }; }

  static getStubConfig() {
    return { location_entity:"", sensor_entities:[], binary_sensor_entities:[], additional_entities:[], show_auto_device_sensors:true, show_tracker_details:true, show_attributes:false, hide_unavailable:true, show_map:true, hours_to_show:24, map_zoom:14, show_route:true, show_statistics:true, show_timeline:true, timeline_items:12, show_sensor_history:false, history_hours:24, sensor_columns:2, compact:false };
  }

  static getConfigForm() {
    return {
      schema: [
        { name:"location_entity", required:true, selector:{ entity:{ domain:"device_tracker" } } },
        { name:"sensor_entities", selector:{ entity:{ domain:"sensor", multiple:true } } },
        { name:"binary_sensor_entities", selector:{ entity:{ domain:"binary_sensor", multiple:true } } },
        { name:"additional_entities", selector:{ entity:{ multiple:true } } },
        { name:"show_auto_device_sensors", selector:{ boolean:{} } },
        { name:"show_tracker_details", selector:{ boolean:{} } },
        { name:"show_attributes", selector:{ boolean:{} } },
        { name:"hide_unavailable", selector:{ boolean:{} } },
        { name:"show_map", selector:{ boolean:{} } },
        { name:"show_route", selector:{ boolean:{} } },
        { name:"hours_to_show", selector:{ number:{ min:1,max:168,step:1,mode:"box" } } },
        { name:"map_zoom", selector:{ number:{ min:1,max:20,step:1,mode:"slider" } } },
        { name:"show_statistics", selector:{ boolean:{} } },
        { name:"show_timeline", selector:{ boolean:{} } },
        { name:"timeline_items", selector:{ number:{ min:4,max:50,step:1,mode:"box" } } },
        { name:"show_sensor_history", selector:{ boolean:{} } },
        { name:"history_hours", selector:{ number:{ min:1,max:168,step:1,mode:"box" } } },
        { name:"sensor_columns", selector:{ number:{ min:1,max:4,step:1,mode:"slider" } } },
        { name:"compact", selector:{ boolean:{} } }
      ],
      computeLabel: (schema) => ({
        location_entity:"Location entity", sensor_entities:"Sensors to display", binary_sensor_entities:"Binary sensors to display", additional_entities:"Any additional entities", show_auto_device_sensors:"Auto-discover sensors from the same device", show_tracker_details:"Show tracker details", show_attributes:"Show entity attributes", hide_unavailable:"Hide unavailable / unknown", show_map:"Show map", show_route:"Show route", hours_to_show:"Map history (hours)", map_zoom:"Map zoom", show_statistics:"Show statistics", show_timeline:"Show timeline", timeline_items:"Timeline items", show_sensor_history:"Show sensor history", history_hours:"Sensor history (hours)", sensor_columns:"Sensor columns", compact:"Compact header"
      })[schema.name]
    };
  }

  _t(key) { const lang = String(this._hass?.language || navigator.language || "en").toLowerCase().split("-")[0]; return (PT_I18N[lang] || PT_I18N.en)[key] || PT_I18N.en[key] || key; }
  _state(id) { return id && this._hass ? this._hass.states[id] : undefined; }
  _escape(v) { return String(v ?? "").replace(/[&<>\"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",\"\" :"&quot;","'":"&#39;"}[c])); }
  _icon(id) { const s=this._state(id); return s?.attributes?.icon || (id?.startsWith("binary_sensor.") ? "mdi:checkbox-marked-circle-outline" : "mdi:chart-line"); }
  _friendlyName(id) { return this._state(id)?.attributes?.friendly_name || id; }
  _deviceId(id) { return this._hass?.entities?.[id]?.device_id || this._hass?.entities?.[id]?.deviceId; }
  _formatNumber(v, digits=1) { const n=Number(v); return Number.isFinite(n) ? n.toFixed(digits) : "—"; }
  _formatDistance(v) { const n=Number(v); if(!Number.isFinite(n)) return "—"; return n < 1000 ? `${n.toFixed(0)} m` : `${(n/1000).toFixed(2)} km`; }
  _formatState(id) { const s=this._state(id); if(!s) return "—"; if(id.startsWith("binary_sensor.")) return s.state === "on" ? this._t("on") : s.state === "off" ? this._t("off") : s.state; const u=s.attributes?.unit_of_measurement; return `${s.state}${u ? ` ${u}` : ""}`; }

  _discoverDeviceEntities() {
    if(!this._hass || this._config?.show_auto_device_sensors === false) return [];
    const loc=this._config?.location_entity, deviceId=this._deviceId(loc);
    if(deviceId && this._hass.entities) return Object.entries(this._hass.entities).filter(([id,r]) => { const d=id.split(".")[0]; return ["sensor","binary_sensor"].includes(d) && r?.device_id===deviceId && this._hass.states[id]; }).map(([id])=>id);
    const prefix=loc?.replace(/^device_tracker\./,"").replace(/_location$/,"");
    return prefix ? Object.keys(this._hass.states).filter(id => ["sensor","binary_sensor"].includes(id.split(".")[0]) && id.startsWith(`${id.split(".")[0]}.${prefix}_`)) : [];
  }

  _configuredEntities() {
    const groups=[this._config?.sensor_entities,this._config?.binary_sensor_entities,this._config?.additional_entities];
    return groups.flatMap(v => Array.isArray(v)?v:(v?[v]:[])).filter(id=>this._state(id));
  }
  _allExtraEntities() {
    return [...new Set([...this._configuredEntities(),...this._discoverDeviceEntities()])].filter(id => { const s=this._state(id); return s && (!this._config?.hide_unavailable || !["unavailable","unknown"].includes(s.state)); });
  }
  _attributes(id) { const a=this._state(id)?.attributes; if(!a) return ""; const ignored=new Set(["friendly_name","unit_of_measurement","icon","device_class","state_class","last_reset","latitude","longitude"]); const rows=Object.entries(a).filter(([k,v])=>!ignored.has(k)&&v!=null&&typeof v!=="object"); return rows.length?`<div class="attributes">${rows.map(([k,v])=>`<div>${this._escape(k)}: ${this._escape(v)}</div>`).join("")}</div>`:""; }

  _renderExtraSensors() {
    const entities=this._allExtraEntities(); if(!entities.length) return "";
    const cols=Math.min(4,Math.max(1,Number(this._config?.sensor_columns||2)));
    return `<div class="section-title">${this._t("data")}</div><div class="sensor-grid" style="--sensor-columns:${cols}">${entities.map(id=>{const s=this._state(id);return `<div class="sensor-item"><ha-icon icon="${this._escape(this._icon(id))}"></ha-icon><div class="sensor-main"><div class="label">${this._escape(this._friendlyName(id))}</div><div class="value">${this._escape(this._formatState(id))}</div>${this._config?.show_attributes?this._attributes(id):""}</div></div>`;}).join("")}</div>`;
  }

  async _loadLocationHistory() {
    if(!this._hass||!this._config?.location_entity||this._historyPromise)return;
    const hours=Math.max(1,Math.min(168,Number(this._config?.hours_to_show||24)));
    this._historyPromise=this._hass.callApi("GET",`history/period?filter_entity_id=${encodeURIComponent(this._config.location_entity)}&minimal_response=false&no_attributes=false&significant_changes_only=false&start_time=${encodeURIComponent(new Date(Date.now()-hours*3600000).toISOString())}`).then(data=>{this._history=Array.isArray(data)?data[0]||[]:[];this._render();}).catch(()=>{this._history=[];}).finally(()=>{this._historyPromise=null;});
  }
  _points() { return (this._history||[]).map(s=>({time:s.last_changed||s.last_updated,state:s.state,lat:Number(s.attributes?.latitude),lon:Number(s.attributes?.longitude),zone:s.attributes?.zone||s.state,movement:s.attributes?.movement,speed:Number(s.attributes?.speed_kmh??s.attributes?.speed),accuracy:Number(s.attributes?.gps_accuracy)})).filter(p=>Number.isFinite(p.lat)&&Number.isFinite(p.lon)); }
  _distance(a,b) { const R=6371,r=Math.PI/180,dLat=(b.lat-a.lat)*r,dLon=(b.lon-a.lon)*r,x=Math.sin(dLat/2)**2+Math.cos(a.lat*r)*Math.cos(b.lat*r)*Math.sin(dLon/2)**2;return R*2*Math.atan2(Math.sqrt(x),Math.sqrt(1-x)); }
  _fmtDuration(s) { if(s>=86400)return `${Math.floor(s/86400)}d ${Math.floor(s%86400/3600)}h`; if(s>=3600)return `${Math.floor(s/3600)}h ${Math.floor(s%3600/60)}m`; return `${Math.floor(s/60)}m`; }

  _statistics() {
    const p=this._points(); if(!p.length)return ""; let distance=0,maxSpeed=0,moving=0,accuracySum=0,accuracyCount=0;
    for(let i=1;i<p.length;i++){distance+=this._distance(p[i-1],p[i]);if(Number.isFinite(p[i].speed))maxSpeed=Math.max(maxSpeed,p[i].speed);if(p[i].movement==="moving"||p[i].movement==="on")moving+=Math.max(0,(new Date(p[i].time)-new Date(p[i-1].time))/1000);if(Number.isFinite(p[i].accuracy)){accuracySum+=p[i].accuracy;accuracyCount++;}}
    const duration=p.length>1?Math.max(0,(new Date(p.at(-1).time)-new Date(p[0].time))/1000):0;
    const cells=[["distance",`${distance<1?distance.toFixed(2):distance.toFixed(1)} km`],["trackingPeriod",this._fmtDuration(duration)],["movingTime",this._fmtDuration(moving)],["maxSpeed",maxSpeed?`${maxSpeed.toFixed(0)} km/h`:"—"],["gpsPoints",p.length],["zones",new Set(p.map(x=>x.zone).filter(Boolean)).size]];
    if(accuracyCount)cells.push(["gpsAccuracy",`${(accuracySum/accuracyCount).toFixed(1)} m`]);
    return `<div class="section-title">${this._t("statistics")}</div><div class="stats-grid">${cells.map(([l,v])=>`<div class="stat"><div class="label">${this._t(l)}</div><div class="big">${this._escape(v)}</div></div>`).join("")}</div>`;
  }

  _timeline() {
    const raw=this._history||[]; if(!raw.length)return ""; const items=Math.max(4,Number(this._config?.timeline_items||12)); const selected=raw.slice(-items).reverse();
    return `<div class="section-title">${this._t("timeline")}</div><div class="timeline">${selected.map(x=>{const a=x.attributes||{},dt=new Date(x.last_changed||x.last_updated),time=Number.isNaN(dt.valueOf())?"—":dt.toLocaleTimeString([], {hour:"2-digit",minute:"2-digit"}),detail=[a.zone||x.state,a.movement,Number.isFinite(Number(a.speed_kmh??a.speed))?`${Number(a.speed_kmh??a.speed).toFixed(0)} km/h`:""].filter(Boolean).join(" · ");return `<div class="timeline-item"><div class="dot"></div><div><div class="timeline-time">${this._escape(time)}</div><div class="timeline-title">${this._escape(a.zone||x.state||this._t("unknown"))}</div><div class="timeline-detail">${this._escape(detail)}</div></div></div>`;}).join("")}</div>`;
  }

  _routeSvg() {
    const p=this._points(); if(p.length<2)return `<div class="route-empty">${this._t("noLocation")}</div>`;
    const minLat=Math.min(...p.map(x=>x.lat)),maxLat=Math.max(...p.map(x=>x.lat)),minLon=Math.min(...p.map(x=>x.lon)),maxLon=Math.max(...p.map(x=>x.lon)),latSpan=Math.max(maxLat-minLat,0.00001),lonSpan=Math.max(maxLon-minLon,0.00001);
    const xy=x=>[12+(x.lon-minLon)/lonSpan*276,12+(maxLat-x.lat)/latSpan*156]; const points=p.map(x=>xy(x).join(",")).join(" "); const start=xy(p[0]),end=xy(p.at(-1));
    return `<div class="route-wrap"><svg viewBox="0 0 300 180" preserveAspectRatio="none" aria-label="${this._escape(this._t("route"))}"><rect x="0" y="0" width="300" height="180" rx="14" fill="var(--card-background-color)" opacity=".35"></rect><polyline points="${points}" fill="none" stroke="var(--primary-color)" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"></polyline><circle cx="${start[0]}" cy="${start[1]}" r="6" fill="var(--primary-color)"></circle><circle cx="${end[0]}" cy="${end[1]}" r="7" fill="var(--accent-color,var(--primary-color))" stroke="white" stroke-width="2"></circle></svg><div class="route-caption">${this._t("route")} · ${p.length} GPS</div></div>`;
  }

  async _renderMap(host) {
    if(!host||!this._hass)return;
    const el="hui-map-card";
    if(!customElements.get(el))await Promise.race([customElements.whenDefined(el),new Promise(r=>setTimeout(r,1800))]);
    if(customElements.get(el)){
      try{const card=document.createElement(el);card.setConfig({type:"map",entities:[this._config.location_entity],hours_to_show:Number(this._config?.hours_to_show||24),default_zoom:Number(this._config?.map_zoom||14),auto_fit:true,theme_mode:"auto"});card.hass=this._hass;host.replaceChildren(card);this._renderedMap=true;return;}catch(_e){}
    }
    host.innerHTML=this._routeSvg(); this._renderedMap=false;
  }

  async _renderHistory(host,entities){if(!host||!this._hass||!entities.length)return;const el="hui-history-graph-card";if(!customElements.get(el))await Promise.race([customElements.whenDefined(el),new Promise(r=>setTimeout(r,1500))]);if(!customElements.get(el))return;try{const card=document.createElement(el);card.setConfig({type:"history-graph",entities,hours_to_show:Number(this._config?.history_hours||24)});card.hass=this._hass;host.replaceChildren(card);}catch(_e){host.replaceChildren();}}

  _render(){
    if(!this._hass||!this._config)return;
    const c=this._config,a=this._state(c.location_entity)?.attributes||{},locState=this._state(c.location_entity), extra=this._allExtraEntities();
    const zone=a.zone||locState?.state||this._t("unknown"), movement=a.movement||"stationary", source=a.source||"—", confidence=Number(a.confidence),gps=Number(a.gps_accuracy),speed=Number(a.speed_kmh??a.speed),distance=a.distance_home;
    this.innerHTML=`<ha-card><div class="card-head"><div class="head-icon"><ha-icon icon="mdi:map-marker-account"></ha-icon></div><div class="head-main"><div class="title">${this._escape(a.friendly_name||this._t("tracker"))}</div><div class="subtitle">${this._escape(zone)} · ${this._escape(movement)}</div></div><div class="status">${this._escape(zone)}</div></div>${c.show_map!==false?`<div class="map-host"></div>`:""}<div class="body">${c.show_route!==false?this._routeSvg():""}${c.show_tracker_details!==false?`<div class="section-title">${this._t("details")}</div><div class="detail-grid">${[["zone",zone],["movement",movement],["source",this._friendlySource(source)],["distanceHome",this._formatDistance(distance)],["sources",a.source_count],["rejectedGps",a.rejected_samples],["confidence",Number.isFinite(confidence)?`${confidence.toFixed(0)} %`:"—"],["gpsAccuracy",Number.isFinite(gps)?`${gps.toFixed(1)} m`:"—"],["speed",Number.isFinite(speed)?`${speed.toFixed(1)} km/h`:"—"],["activeSources",a.active_sources??a.source_count],["rejectedSamples",a.rejected_samples],["moving",movement]].filter(x=>x[1]!=null&&x[1]!=="").map(([l,v])=>`<div class="detail-item"><div class="label">${this._t(l)}</div><div class="value">${this._escape(v)}</div></div>`).join("")}</div>`:""}${this._renderExtraSensors()}${c.show_statistics!==false?this._statistics():""}${c.show_timeline!==false?this._timeline():""}${c.show_sensor_history&&extra.length?`<div class="section-title">${this._t("sensorHistory")}</div><div class="history-host"></div>`:""}</div></ha-card>`;
    const mapHost=this.querySelector(".map-host"); if(mapHost)this._renderMap(mapHost);
    const historyHost=this.querySelector(".history-host"); if(historyHost)this._renderHistory(historyHost,extra.slice(0,12));
  }

  _friendlySource(source){ if(!source||source==="—")return source; const s=this._state(source); return s?.attributes?.friendly_name||source.replace(/^(device_tracker|sensor|binary_sensor)\./,"").replaceAll("_"," "); }
}

if(!customElements.get("person-tracker-pro-card"))customElements.define("person-tracker-pro-card",PersonTrackerProCard);
window.customCards=window.customCards||[];
if(!window.customCards.some(c=>c.type==="person-tracker-pro-card"))window.customCards.push({type:"person-tracker-pro-card",name:"Person Tracker PRO",description:"Advanced Person Tracker PRO card with map, route, statistics and device sensors",preview:true});
