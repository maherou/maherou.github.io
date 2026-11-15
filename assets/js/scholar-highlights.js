// Renders the Publications lists on the home page from scholar_highlights.json
// (written by scripts/fetch_scholar.py). Built with createElement/textContent,
// never innerHTML, because the data comes from an outside source. If the file
// is missing or malformed, the section shows only the Google Scholar link.
//
// Copyright (c) 2026 Michael A. Heroux. Code under the MIT License.
(function () {
  var root = document.querySelector('.pubs');
  if (!root) return;
  var section = root.closest('section');
  var fallback = section.querySelector('.pubs-fallback');
  var link = section.querySelector('[data-scholar-link]');
  var updated = section.querySelector('.pubs-updated');

  function safeUrl(u) {
    return typeof u === 'string' && /^https?:\/\//i.test(u) ? u : null;
  }

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text) n.textContent = text;
    return n;
  }

  // Site owner's name: always shown, in bold, even when a long author list
  // is shortened to "et al."
  var OWNER = /Heroux/;

  function authorLine(text) {
    var names = text.split(', ');
    var shown = names;
    if (names.length > 8) {
      shown = names.slice(0, 6);
      var owner = names.filter(function (n) { return OWNER.test(n); })[0];
      if (owner && !shown.some(function (n) { return OWNER.test(n); })) {
        shown = names.slice(0, 5).concat(['\u2026', owner]);
      }
      shown = shown.concat(['et al.']);
    }
    var div = el('div', 'pub-authors');
    shown.forEach(function (n, i) {
      if (i) div.appendChild(document.createTextNode(', '));
      if (OWNER.test(n)) div.appendChild(el('strong', null, n));
      else div.appendChild(document.createTextNode(n));
    });
    return div;
  }

  function item(p) {
    var li = el('li', 'pub');
    var title = String(p.title || '');
    var url = safeUrl(p.url);
    var t;
    if (url) {
      t = el('a', 'pub-title', title);
      t.href = url;
      t.target = '_blank';
      t.rel = 'noopener';
    } else {
      t = el('span', 'pub-title', title);
    }
    li.appendChild(t);

    if (p.authors) li.appendChild(authorLine(String(p.authors)));

    var venue = String(p.venue || '');
    var year = Number(p.year) > 0 ? String(p.year) : '';
    var where = venue;
    if (year && venue.indexOf(year) === -1) where = venue ? venue + ', ' + year : year;
    var meta = el('div', 'pub-meta');
    if (where) meta.appendChild(el('span', null, where));
    var cites = Number(p.citations);
    if (cites >= 0 && isFinite(cites)) {
      meta.appendChild(el('span', 'pub-cites',
        cites.toLocaleString('en-US') + (cites === 1 ? ' citation' : ' citations')));
    }
    li.appendChild(meta);
    return li;
  }

  fetch(root.getAttribute('data-src'), { cache: 'no-cache' })
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(function (data) {
      var shown = 0;
      root.querySelectorAll('[data-list]').forEach(function (ol) {
        var list = Array.isArray(data[ol.getAttribute('data-list')]) ? data[ol.getAttribute('data-list')] : [];
        list.forEach(function (p) { if (p && p.title) { ol.appendChild(item(p)); shown++; } });
        if (!ol.children.length) ol.closest('.pubs-group').hidden = true;
      });
      if (!shown) return;
      var profile = safeUrl(data.profile_url);
      if (profile) link.href = profile;
      if (data.updated) {
        updated.textContent = 'Updated ' + String(data.updated);
        updated.hidden = false;
      }
      root.hidden = false;
      fallback.hidden = true;
    })
    .catch(function () { /* keep the fallback: link only */ });
})();
