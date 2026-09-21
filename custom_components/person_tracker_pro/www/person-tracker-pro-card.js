// Compatibility loader for older Lovelace resource URLs.
(() => {
  const src = '/api/person_tracker_pro/person-tracker-pro-card-v2.js?v=0.4.2';
  const finish = () => {
    if (!customElements.get('person-tracker-pro-card')) {
      const Base = customElements.get('person-tracker-pro-card-v2');
      if (Base) customElements.define('person-tracker-pro-card', class extends Base {});
    }
    window.customCards = window.customCards || [];
    if (!window.customCards.some((x) => x.type === 'person-tracker-pro-card')) {
      window.customCards.push({
        type: 'person-tracker-pro-card',
        name: 'Person Tracker PRO GPS Tracker',
        description: 'GPS tracker card',
        preview: false,
        getEntitySuggestion: (hass, entityId) => entityId?.startsWith('device_tracker.')
          ? { config: { type: 'custom:person-tracker-pro-card', location_entity: entityId } }
          : null,
      });
    }
  };
  if (customElements.get('person-tracker-pro-card-v2')) {
    finish();
    return;
  }
  const existing = [...document.scripts].find((s) => s.src.includes('person-tracker-pro-card-v2.js'));
  if (existing) {
    customElements.whenDefined('person-tracker-pro-card-v2').then(finish).catch((e) => console.error('Person Tracker PRO:', e));
    return;
  }
  const script = document.createElement('script');
  script.src = src;
  script.async = false;
  script.onload = () => customElements.whenDefined('person-tracker-pro-card-v2').then(finish).catch((e) => console.error('Person Tracker PRO:', e));
  script.onerror = (e) => console.error('Person Tracker PRO card load failed', e);
  document.head.appendChild(script);
})();
