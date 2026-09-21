(() => {
  const load = () => new Promise((resolve, reject) => {
    const src = '/api/person_tracker_pro/person-tracker-pro-card-v2.js?v=0.4.1';
    const existing = [...document.scripts].find(s => s.src.includes('person-tracker-pro-card-v2.js'));
    if (existing) {
      customElements.whenDefined('person-tracker-pro-card-v2').then(resolve).catch(reject);
      return;
    }
    const script = document.createElement('script');
    script.src = src;
    script.async = false;
    script.onload = () => customElements.whenDefined('person-tracker-pro-card-v2').then(resolve).catch(reject);
    script.onerror = reject;
    document.head.appendChild(script);
  });
  load().then(() => {
    if (!customElements.get('person-tracker-pro-card')) {
      const Base = customElements.get('person-tracker-pro-card-v2');
      class PersonTrackerProCardAlias extends Base {}
      customElements.define('person-tracker-pro-card', PersonTrackerProCardAlias);
    }
    window.customCards = window.customCards || [];
    if (!window.customCards.some(x => x.type === 'person-tracker-pro-card')) {
      window.customCards.push({
        type: 'person-tracker-pro-card',
        name: 'Person Tracker PRO GPS Tracker',
        description: 'Stable GPS tracker card',
        preview: false,
        getEntitySuggestion: (hass, entityId) => entityId?.startsWith('device_tracker.')
          ? { type: 'custom:person-tracker-pro-card', location_entity: entityId }
          : null,
      });
    }
  }).catch(err => console.error('Person Tracker PRO card loader:', err));
})();
