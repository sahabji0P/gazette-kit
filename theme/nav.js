/* gazette-kit — nav highlight + embed chrome (story pages inside the reader) */
(function () {
  const params = new URLSearchParams(location.search);
  const embedded = params.get('embed') === '1' || window.self !== window.top;
  if (embedded) {
    document.documentElement.classList.add('embed');
    document.body.classList.add('embed');
  }
  const page = (location.pathname.split('/').pop() || 'index.html');
  document.querySelectorAll('.nav-bar a[data-nav]').forEach(a => {
    if (a.getAttribute('data-nav') === page) a.classList.add('active');
  });
})();
