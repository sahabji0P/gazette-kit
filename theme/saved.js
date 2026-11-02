/* gazette-kit — the Saved shelf page */
(function () {
  const catalog = window.GAZETTE_CATALOG || { stories: [], taxonomy: [] };
  const grid = document.getElementById('saved-grid');
  const empty = document.getElementById('saved-empty');
  const countEl = document.getElementById('saved-count');
  const filterEl = document.getElementById('saved-filter');
  let active = null;
  function esc(s) {
    return String(s || '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  }
  function render() {
    const ids = GazetteSave.read();
    const byId = Object.fromEntries((catalog.stories || []).map(s => [s.id, s]));
    const all = ids.map(id => byId[id]).filter(Boolean);
    const items = active ? all.filter(s => (s.categories || []).includes(active)) : all;
    countEl.textContent = String(items.length) + (active ? ' · ' + active : '');
    const counts = new Map();
    all.forEach(s => (s.categories || []).forEach(c => counts.set(c, (counts.get(c) || 0) + 1)));
    const tax = catalog.taxonomy || [];
    const cats = tax.filter(c => counts.has(c)).concat([...counts.keys()].filter(c => !tax.includes(c)));
    filterEl.innerHTML = cats.length
      ? `<button type="button" class="cat-chip${active ? '' : ' voice'}" data-filter="">All</button>` +
        cats.map(c => `<button type="button" class="cat-chip${active === c ? ' voice' : ''}" data-filter="${esc(c)}">${esc(c)} · ${counts.get(c)}</button>`).join('')
      : '';
    filterEl.querySelectorAll('[data-filter]').forEach(b => b.addEventListener('click', () => { active = b.dataset.filter || null; render(); }));
    if (!items.length) { grid.innerHTML = ''; empty.classList.remove('hidden'); return; }
    empty.classList.add('hidden');
    grid.innerHTML = items.map(s => `
      <article class="saved-card">
        <div class="cat-row">${(s.categories || []).map(c => `<span class="cat-chip">${esc(c)}</span>`).join('')}</div>
        <h2 class="hed"><a href="reader.html?id=${esc(s.id)}">${esc(s.headline)}</a></h2>
        <p class="dek">${esc(s.dek)}</p>
        <div class="story-actions"><a class="jump" href="reader.html?id=${esc(s.id)}">Read</a>${GazetteSave.buttonHTML(s.id)}</div>
      </article>`).join('');
  }
  window.addEventListener('gazette-saved-change', render);
  render();
})();
