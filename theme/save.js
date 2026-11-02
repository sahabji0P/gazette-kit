/* gazette-kit — saved shelf (browser localStorage only; nothing leaves the machine).
   Keys come from window.GAZETTE_SITE (written by build.py from gazette.config.json). */
(function (global) {
  const SITE = global.GAZETTE_SITE || { slug: 'gazette', agentSaved: [] };
  const KEY = SITE.slug + '.saved.v1';
  const SEEDED_KEY = SITE.slug + '.agentSeeded.v1';
  /* Agent saves: ids in gazette.config.json → saves.agent_saved. Each id is seeded once,
     so if the reader unsaves it later, it stays unsaved. */
  const AGENT_SAVED = SITE.agentSaved || [];

  function read() {
    try {
      const arr = JSON.parse(localStorage.getItem(KEY) || '[]');
      return Array.isArray(arr) ? arr : [];
    } catch (e) { return []; }
  }
  function write(ids) {
    localStorage.setItem(KEY, JSON.stringify(ids));
    global.dispatchEvent(new CustomEvent('gazette-saved-change', { detail: { ids } }));
  }
  function isSaved(id) { return read().includes(id); }
  function toggle(id) {
    if (!id) return false;
    const ids = read();
    const i = ids.indexOf(id);
    if (i >= 0) ids.splice(i, 1); else ids.unshift(id);
    write(ids);
    return ids.includes(id);
  }
  function esc(s) {
    return String(s || '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  }
  function buttonHTML(id, opts) {
    opts = opts || {};
    const on = isSaved(id);
    const cls = 'save-btn' + (on ? ' is-saved' : '') + (opts.compact ? ' save-btn-compact' : '');
    return `<button type="button" class="${cls}" data-save-id="${esc(id)}" aria-pressed="${on}" title="${on ? 'Remove from Saved' : 'Save for later'}">${on ? 'Saved' : 'Save'}</button>`;
  }
  function paint(btn, on) {
    btn.classList.toggle('is-saved', on);
    btn.setAttribute('aria-pressed', on ? 'true' : 'false');
    btn.textContent = on ? 'Saved' : 'Save';
  }
  function bind(root) {
    (root || document).addEventListener('click', function (e) {
      const btn = e.target.closest('[data-save-id]');
      if (!btn) return;
      e.preventDefault();
      e.stopPropagation();
      paint(btn, toggle(btn.getAttribute('data-save-id')));
    });
  }
  function refreshAll(root) {
    (root || document).querySelectorAll('[data-save-id]').forEach(btn => paint(btn, isSaved(btn.getAttribute('data-save-id'))));
  }
  function seedAgentSaves() {
    try {
      const seeded = JSON.parse(localStorage.getItem(SEEDED_KEY) || '[]');
      const fresh = AGENT_SAVED.filter(id => !seeded.includes(id));
      if (!fresh.length) return;
      const ids = read();
      fresh.slice().reverse().forEach(id => { if (!ids.includes(id)) ids.unshift(id); });
      localStorage.setItem(SEEDED_KEY, JSON.stringify(seeded.concat(fresh)));
      write(ids);
    } catch (e) {}
  }

  global.GazetteSave = { read, write, isSaved, toggle, buttonHTML, bind, refreshAll, KEY };
  seedAgentSaves();
  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-story-id] .story-actions').forEach(slot => {
      if (slot.querySelector('[data-save-id]')) return;
      const host = slot.closest('[data-story-id]');
      slot.insertAdjacentHTML('beforeend', buttonHTML(host.getAttribute('data-story-id')));
    });
    bind(document);
    refreshAll(document);
  });
})(window);
