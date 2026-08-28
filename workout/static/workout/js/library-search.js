document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('exercise-search');
  const cards = [...document.querySelectorAll('#exercise-grid .exercise-card')];
  const count = document.getElementById('exercise-results-count');
  const empty = document.getElementById('live-search-empty');
  if (!input || !count || !empty) return;

  const applySearch = () => {
    const term = input.value.trim().toLowerCase();
    let visible = 0;
    cards.forEach(card => {
      const matches = !term || card.dataset.search.toLowerCase().includes(term);
      card.hidden = !matches;
      if (matches) visible += 1;
    });
    count.textContent = `${visible} exercise${visible === 1 ? '' : 's'}`;
    empty.hidden = visible !== 0;
    const url = new URL(window.location.href);
    if (term) url.searchParams.set('q', input.value.trim()); else url.searchParams.delete('q');
    window.history.replaceState({}, '', url);
  };

  input.addEventListener('input', applySearch);
});
