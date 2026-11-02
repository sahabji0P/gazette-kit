/* gazette-kit — split reader: story list on one side, the story page on the other. */
(function () {
  const SITE = window.GAZETTE_SITE || { name: 'Gazette' };
  const LIST = document.getElementById('list-pane');
  const FRAME = document.getElementById('detail-frame');
  const DETAIL = document.getElementById('detail-fallback');
  let catalog = null;
  let selectedId = null;

  function esc(s) {
    return String(s || '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  }
  function chips(cats) {
    return (cats || []).map(c => `<span class="cat-chip">${esc(c)}</span>`).join('');
  }
  function readable() {
    const rank = { lead: 0, confirmed: 1, brief: 2, rumor: 3 };
    return (catalog.stories || [])
      .filter(s => s.body_path && s.status !== 'archive')
      .sort((a, b) => {
        const ra = a.id === catalog.lead ? -1 : (rank[a.status] ?? 5);
        const rb = b.id === catalog.lead ? -1 : (rank[b.status] ?? 5);
        if (ra !== rb) return ra - rb;
        if ((b.strike || 0) !== (a.strike || 0)) return (b.strike || 0) - (a.strike || 0);
        return (b.date || '').localeCompare(a.date || '');
      });
  }
  function actions(story) {
    const slot = document.getElementById('reader-actions');
    if (!slot) return;
    slot.innerHTML = story && window.GazetteSave
      ? `<div class="cat-row">${chips(story.categories)}</div>` + GazetteSave.buttonHTML(story.id) : '';
  }
  function renderList() {
    LIST.innerHTML = readable().map(s => {
      const badge = s.status === 'lead' ? '<span class="mail-badge">lead</span>'
        : s.status === 'brief' ? '<span class="mail-badge rumor">idea</span>'
        : s.status === 'rumor' ? '<span class="mail-badge rumor">rumor</span>' : '';
      const lines = (s.what_happened || []).slice(0, 2).map(t => `<li>${esc(t)}</li>`).join('');
      const save = window.GazetteSave ? GazetteSave.buttonHTML(s.id, { compact: true }) : '';
      return `<button type="button" class="mail-card${s.id === selectedId ? ' selected' : ''}" data-id="${esc(s.id)}">
        <div class="mail-card-top"><span class="mail-kicker">${esc(s.section_label)}</span>${badge}</div>
        <div class="mail-hed">${esc(s.headline)}</div>
        <div class="cat-row">${chips(s.categories)}</div>
        <ul class="mail-tldr">${lines}</ul>
        <div class="story-actions" onclick="event.stopPropagation()">${save}</div>
      </button>`;
    }).join('') || '<p class="empty">No stories yet.</p>';
    LIST.querySelectorAll('.mail-card').forEach(btn => btn.addEventListener('click', () => select(btn.dataset.id, true)));
  }
  function select(id, push) {
    const story = (catalog.stories || []).find(s => s.id === id && s.body_path);
    if (!story) {
      FRAME.classList.add('hidden');
      DETAIL.classList.remove('hidden');
      DETAIL.innerHTML = '<p class="empty">Story not found. <a href="index.html">← Front</a></p>';
      return;
    }
    selectedId = story.id;
    actions(story);
    if (push) {
      const url = new URL(location.href);
      url.searchParams.set('id', story.id);
      history.replaceState(null, '', url);
    }
    document.title = story.headline + ' — ' + SITE.name;
    renderList();
    FRAME.classList.remove('hidden');
    DETAIL.classList.add('hidden');
    FRAME.src = story.body_path + '?embed=1';
  }
  catalog = window.GAZETTE_CATALOG;
  if (!catalog) { LIST.innerHTML = '<p class="empty">Could not load the catalog (assets/catalog.js).</p>'; return; }
  const sub = document.querySelector('.reader-sub');
  if (sub && catalog.edition_label) sub.textContent = 'Split reader · ' + catalog.edition_label;
  renderList();
  const id = new URLSearchParams(location.search).get('id') || catalog.lead;
  if (id) select(id, false);
})();
