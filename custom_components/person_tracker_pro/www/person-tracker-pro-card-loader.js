(() => {
  const CARD = 'person-tracker-pro-card';
  const SRC = '/api/person_tracker_pro/person-tracker-pro-card-v2.js?v=0.5.3';

  window.customCards = window.customCards || [];
  if (!window.customCards.some((item) => item.type === CARD)) {
    window.customCards.push({
      type: CARD,
      name: 'Person Tracker PRO GPS Tracker',
      description: 'GPS tracker card',
      preview: true,
      getEntitySuggestion: (hass, entityId) => entityId?.startsWith('device_tracker.')
        ? { config: { type: `custom:${CARD}`, location_entity: entityId } }
        : null,
    });
  }

  // Compatibility loader for old manually-added Lovelace resources.
  // Never waits on customElements.whenDefined(): a failed module must not
  // leave the card picker/editor in an infinite loading state.
  if (!customElements.get(CARD)) {
    const existing = [...document.scripts].find((s) => s.src.includes('person-tracker-pro-card-v2.js'));
    if (!existing) {
      const script = document.createElement('script');
      script.src = SRC;
      script.async = false;
      script.onerror = (error) => console.error('Person Tracker PRO card: failed to load', SRC, error);
      document.head.appendChild(script);
    }
  }

  window.dispatchEvent(new Event('custom-cards-updated'));
})();
