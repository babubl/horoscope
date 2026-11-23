/* Suba Jathagam — shared by every page: colour theme and day/night mode, the appearance picker,
   and an app-like back button (back always returns to the home page, and from home it leaves). */
(function () {
  'use strict';
  var d = document.documentElement;
  var LS = { get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } }, set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} } };
  var SS = { get: function (k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } }, set: function (k, v) { try { sessionStorage.setItem(k, v); } catch (e) {} }, del: function (k) { try { sessionStorage.removeItem(k); } catch (e) {} } };
  var lang = (d.lang || 'en').slice(0, 2);

  // ------------------------------------------------------------------ theme
  var PALS = [
    ['mayil', '#0d4b58', '#e9c46a'], ['kumkum', '#6e1216', '#f0c35a'], ['chandanam', '#7a4a24', '#f2cf7a'],
    ['thamarai', '#7e2650', '#f3c66b'], ['thulasi', '#2c5627', '#e8cf72'], ['neelam', '#22336c', '#f0c860']
  ];
  var TX = {
    en: { look: 'Appearance', mode: 'Day / night', auto: 'Auto', light: 'Day', dark: 'Night', pal: 'App colour', music: 'Music', off: 'Off', close: 'Close',
          mayil: 'Peacock', kumkum: 'Kumkum', chandanam: 'Sandal', thamarai: 'Lotus', thulasi: 'Tulsi', neelam: 'Neelam' },
    ta: { look: 'தோற்றம்', mode: 'பகல் / இரவு', auto: 'தானாக', light: 'பகல்', dark: 'இரவு', pal: 'செயலி நிறம்', music: 'இசை', off: 'நிறுத்து', close: 'மூடு',
          mayil: 'மயில்', kumkum: 'குங்குமம்', chandanam: 'சந்தனம்', thamarai: 'தாமரை', thulasi: 'துளசி', neelam: 'நீலம்' },
    te: { look: 'రూపం', mode: 'పగలు / రాత్రి', auto: 'ఆటో', light: 'పగలు', dark: 'రాత్రి', pal: 'యాప్ రంగు', music: 'సంగీతం', off: 'ఆపు', close: 'మూసివేయి',
          mayil: 'నెమలి', kumkum: 'కుంకుమ', chandanam: 'చందనం', thamarai: 'తామర', thulasi: 'తులసి', neelam: 'నీలం' }
  };
  var T = TX[lang] || TX.en;
  var mq = window.matchMedia ? matchMedia('(prefers-color-scheme: dark)') : null;
  function mode() { return LS.get('sj.mode') || 'auto'; }
  function pal() { var p = LS.get('sj.pal'); return PALS.some(function (x) { return x[0] === p; }) ? p : 'mayil'; }
  function apply() {
    var m = mode(), k = m === 'auto' ? (mq && mq.matches ? 'dark' : 'light') : m;
    d.setAttribute('data-theme', k);
    d.setAttribute('data-pal', pal());
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) { var c = getComputedStyle(d).getPropertyValue('--maroon').trim(); if (c) meta.setAttribute('content', c); }
    document.querySelectorAll('[data-look]').forEach(render);
  }
  if (mq && mq.addEventListener) mq.addEventListener('change', function () { if (mode() === 'auto') apply(); });
  window.addEventListener('storage', function (e) { if (e.key === 'sj.mode' || e.key === 'sj.pal') apply(); });

  // the picker: day/night, colour and (where the music runs) the music choice
  function render(box) {
    var m = mode(), p = pal(), M = window.SJMusic, h;
    if (box.getAttribute('data-look') === 'music') {
      if (!M) { box.innerHTML = ''; return; }
      var c0 = M.current();
      box.innerHTML = '<div class="look"><div class="tracks">' + M.tracks().map(function (x) {
        return '<button type="button" data-track="' + x.id + '" aria-pressed="' + (M.playing() && c0 === x.id) + '">' + x.icon + ' ' + x.name + '</button>';
      }).join('') + '<button type="button" data-track="off" aria-pressed="' + !M.playing() + '">🔇 ' + T.off + '</button></div></div>';
      return;
    }
    h = '<div class="look"><p class="lk">' + T.mode + '</p><div class="seg3">' +
      ['auto', 'light', 'dark'].map(function (x) { return '<button type="button" data-mode="' + x + '" aria-pressed="' + (x === m) + '">' + (x === 'auto' ? '◐ ' : x === 'light' ? '☀ ' : '☾ ') + T[x] + '</button>'; }).join('') +
      '</div><p class="lk">' + T.pal + '</p><div class="pals">' +
      PALS.map(function (x) { return '<button type="button" data-pal="' + x[0] + '" aria-pressed="' + (x[0] === p) + '"><i style="background:linear-gradient(135deg,' + x[1] + ' 60%,' + x[2] + ' 60%)"></i>' + T[x[0]] + '</button>'; }).join('') + '</div>';
    if (M && M.tracks) {
      var cur = M.current();
      h += '<p class="lk">' + T.music + '</p><div class="tracks">' + M.tracks().map(function (x) {
        return '<button type="button" data-track="' + x.id + '" aria-pressed="' + (M.playing() && cur === x.id) + '">' + x.icon + ' ' + x.name + '</button>';
      }).join('') + '<button type="button" data-track="off" aria-pressed="' + !M.playing() + '">🔇 ' + T.off + '</button></div>';
    }
    box.innerHTML = h + '</div>';
  }
  window.SJLook = { render: function () { document.querySelectorAll('[data-look]').forEach(render); } };
  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-look] [data-mode], [data-look] [data-pal], [data-look] [data-track]');
    if (b) {
      e.preventDefault();
      if (b.dataset.mode) LS.set('sj.mode', b.dataset.mode);
      else if (b.dataset.pal) LS.set('sj.pal', b.dataset.pal);
      else if (window.SJMusic) { if (b.dataset.track === 'off') window.SJMusic.stop(); else window.SJMusic.play(b.dataset.track); }
      apply(); return;
    }
    var lb = e.target.closest('[data-look-open]');
    if (lb) { e.preventDefault(); openPop(lb); return; }
    if (e.target.closest('[data-look-close]')) { closePop(); return; }
    var pop = document.getElementById('lookPop');
    if (pop && !pop.hidden && !e.target.closest('#lookPop')) closePop();
  });
  function openPop(btn) {
    var pop = document.getElementById('lookPop');
    if (!pop) {
      pop = document.createElement('div'); pop.id = 'lookPop'; pop.className = 'lookpop'; pop.setAttribute('role', 'dialog'); pop.setAttribute('aria-label', T.look);
      pop.innerHTML = '<h4><span></span><button type="button" data-look-close aria-label="' + T.close + '">✕</button></h4><div data-look></div>';
      document.body.appendChild(pop);
    }
    var kind = btn.getAttribute('data-look-open') === 'music' ? 'music' : '';
    if (!pop.hidden && pop.getAttribute('data-kind') === kind) { closePop(); return; }
    pop.setAttribute('data-kind', kind);
    pop.querySelector('h4 span').textContent = kind ? T.music : T.look;
    var box = pop.querySelector('[data-look]'); box.setAttribute('data-look', kind);
    pop.hidden = false; render(box);
    var r = btn.getBoundingClientRect(); pop.style.top = Math.round(r.bottom + 8) + 'px';
  }
  function closePop() { var pop = document.getElementById('lookPop'); if (pop) pop.hidden = true; }
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closePop(); });
  apply();

  // ------------------------------------------------------------------ back button
  // Home is the app page (/, /ta/, /te/ …). Leaving home adds one history entry; moving between other pages
  // replaces it, so Back always lands on home, and Back on home leaves the app.
  var HOME_RE = /^\/((ta|te|ml|kn|hi)\/)?(index\.html)?$/;
  var isHome = HOME_RE.test(location.pathname);
  function onHomeShow() {
    if (!isHome) return;
    SS.del('sj.back');
    var g = SS.get('sj.goto'); SS.del('sj.goto');
    if (g === null) return;
    var tab = /^#horo/.test(g) ? 'horo' : /^#match/.test(g) ? 'match' : 'home';
    var b = document.querySelector('.tabs button[data-tab="' + tab + '"]');
    if (b && !b.classList.contains('on')) b.click();
    if (/^#feedback$/.test(g)) { var f = document.querySelector('[data-fb-open]'); if (f) f.click(); }
    window.scrollTo(0, 0);
  }
  window.addEventListener('pageshow', onHomeShow);
  document.addEventListener('click', function (e) {
    if (e.defaultPrevented || e.button || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var a = e.target.closest('a[href]');
    if (!a || (a.target && a.target !== '_self') || a.hasAttribute('download')) return;
    var u; try { u = new URL(a.getAttribute('href'), location.href); } catch (x) { return; }
    if (u.origin !== location.origin || !/^https?:$/.test(u.protocol)) return;
    if (/\.(ics|pdf|png|jpg|webp|zip)$/i.test(u.pathname)) return;
    // a link within this page: scroll, without adding a step to the history
    if (u.pathname === location.pathname && u.search === location.search) {
      if (!u.hash || u.hash === '#') return;
      var el = null; try { el = document.getElementById(decodeURIComponent(u.hash.slice(1))); } catch (x) {}
      if (el && !el.matches('.tabs *')) { e.preventDefault(); el.scrollIntoView({ behavior: 'smooth', block: 'start' }); history.replaceState(history.state, '', u.hash); }
      return;
    }
    if (isHome) { SS.set('sj.back', location.pathname); return; }   // leaving home: a normal step back to it
    e.preventDefault();
    var prevHome = SS.get('sj.back');
    if (HOME_RE.test(u.pathname) && prevHome === u.pathname && u.hash.indexOf('=') < 0) {
      SS.set('sj.goto', u.hash || '#'); history.back();             // home is the page behind this one: go back to it
      return;
    }
    location.replace(u.href);
  });
})();
