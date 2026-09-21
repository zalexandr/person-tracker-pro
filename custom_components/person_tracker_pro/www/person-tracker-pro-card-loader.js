(() => {
  const CARD = 'person-tracker-pro-card';
  const V2 = 'person-tracker-pro-card-v2';
  const SRC = '/api/person_tracker_pro/person-tracker-pro-card-v2.js?v=0.4.2';

  const register = () => {
    if (!customElements.get(CARD)) {
      const Base = customElements.get(V2);
      if (Base) {
        class PersonTrackerProCardAlias extends Base {}
        customElements.define(CARD, PersonTrackerProCardAlias);
      }
    }
    window.customCards = window.customCards || [];
    if (!window.customCards.some((item) => item.type === CARD)) {
      window.customCards.push({
        type: CARD,
        name: 'Person Tracker PRO GPS Tracker',
        description: 'GPS tracker card',
        preview: false,
        getEntitySuggestion: (hass, entityId) => entityId?.startsWith('device_tracker.')
          ? { type: `custom:${CARD}`, location_entity: entityId }
          : null,
      });
    }
  };

  const load = () => {
    if (customElements.get(V2)) return Promise.resolve();
    const existing = [...document.scripts].find((s) => s.src.includes(V2));
    if (existing) return customElements.whenDefined(V2);
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = SRC;
      script.onload = () => customElements.whenDefined(V2).then(resolve).catch(reject);
      script.onerror = reject;
      document.head.appendChild(script);
    });
  };

  load().then(() => {
    register();
    window.dispatchEvent(new Event('custom-cards-updated'));
  }).catch((error) => console.error('Person Tracker PRO card loader:', error));
})();
