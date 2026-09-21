// Compatibility loader for older Lovelace resource URLs.
(() => {
  const CARD = 'person-tracker-pro-card';
  const V2 = 'person-tracker-pro-card-v2';
  const SRC = '/api/person_tracker_pro/person-tracker-pro-card-v2.js?v=0.4.3';

  window.customCards = window.customCards || [];
  if (!window.customCards.some((item) => item.type === CARD)) {
    window.customCards.push({
      type: CARD,
      name: 'Person Tracker PRO GPS Tracker',
      description: 'GPS tracker card',
      preview: true,
      getEntitySuggestion: (hass, entityId) => entityId?.startsWith('device_tracker.')
        ? { type: `custom:${CARD}`, location_entity: entityId }
        : null,
    });
  }

  const finish = () => {
    if (!customElements.get(CARD)) {
      const Base = customElements.get(V2);
      if (Base) customElements.define(CARD, class extends Base {});
    }
    window.dispatchEvent(new Event('custom-cards-updated'));
  };

  if (customElements.get(V2)) {
    finish();
    return;
  }

  const existing = [...document.scripts].find((s) => s.src.includes('person-tracker-pro-card-v2.js'));
  if (existing) {
    customElements.whenDefined(V2).then(finish).catch((e) => console.error('Person Tracker PRO:', e));
    return;
  }

  const script = document.createElement('script');
  script.src = SRC;
  script.async = false;
  script.onload = () => customElements.whenDefined(V2).then(finish).catch((e) => console.error('Person Tracker PRO:', e));
  script.onerror = () => console.error(`Person Tracker PRO card load failed: ${SRC}`);
  document.head.appendChild(script);
})();
