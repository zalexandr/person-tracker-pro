(() => {
  const CARD = 'person-tracker-pro-card';
  const V2 = 'person-tracker-pro-card-v2';
  const SRC = '/api/person_tracker_pro/person-tracker-pro-card-v2.js?v=0.4.3';

  window.customCards = window.customCards || [];

  // Register the picker metadata immediately. Do not wait for the lazy-loaded
  // element: HA can open the card picker before the custom element finishes loading.
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

  const registerElementAlias = () => {
    if (customElements.get(CARD)) return;
    const Base = customElements.get(V2);
    if (!Base) return;
    class PersonTrackerProCardAlias extends Base {}
    customElements.define(CARD, PersonTrackerProCardAlias);
  };

  const load = () => {
    if (customElements.get(V2)) return Promise.resolve();
    const existing = [...document.scripts].find((s) => s.src.includes('person-tracker-pro-card-v2.js'));
    if (existing) return customElements.whenDefined(V2);
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = SRC;
      script.async = false;
      script.onload = () => customElements.whenDefined(V2).then(resolve).catch(reject);
      script.onerror = () => reject(new Error(`Failed to load ${SRC}`));
      document.head.appendChild(script);
    });
  };

  load().then(() => {
    registerElementAlias();
    window.dispatchEvent(new Event('custom-cards-updated'));
  }).catch((error) => console.error('Person Tracker PRO card loader:', error));
})();
