/* Suba Jathagam — the calendar's day sheet: today's details open by default (like a daily sheet calendar),
   tap any date in the month to see that day, step a day back or forward. Runs on the calendar pages with
   /assets/panch.js (astronomy, engine and the panchangam widget). Nothing here adds steps to the history. */
(function () {
  'use strict';
  var C = window.SJ_CAL, box = document.getElementById('daysheet');
  if (!C || !box || !window.Jothidam || !window.SJPanch) return;
  var J = window.Jothidam, W = window.SJPanch, D = C.D;
  var place = C.home;
  try { var v = JSON.parse(localStorage.getItem('sj.panchPlace') || 'null'); if (v && isFinite(v.lat) && v.tz) place = v; } catch (e) {}
  var placeName = (C.lang === 'ta' && place.ta) || (place.nat && C.natIdx != null && place.nat[C.natIdx]) || place.name || '';
  function ymdStr(a) { return a[0] + '-' + String(a[1]).padStart(2, '0') + '-' + String(a[2]).padStart(2, '0'); }
  function parse(s) { return s.split('-').map(Number); }
  function shift(s, n) { var a = parse(s), x = new Date(Date.UTC(a[0], a[1] - 1, a[2] + n)); return x.toISOString().slice(0, 10); }
  var today = ymdStr(W.todayYMD(place.tz || 'Asia/Kolkata'));
  var sel = today;
  if (C.month && today.slice(0, 7) !== C.month) sel = C.month + '-01';
  function clock(ms, off) { if (!ms) return '—'; var d = new Date(Math.round((ms + off * 60000) / 60000) * 60000); return String(d.getUTCHours()).padStart(2, '0') + ':' + String(d.getUTCMinutes()).padStart(2, '0'); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  function render() {
    var a = parse(sel), p;
    try { p = J.dailyPanchang({ y: a[0], m: a[1], d: a[2], lat: +place.lat, lon: +place.lon, zone: place.tz }); } catch (e) { box.innerHTML = ''; return; }
    var off = p.offset, dayOf = function (x) { return Math.floor((x + off * 60000) / 86400000); };
    var ck = function (ms) { return clock(ms, off) + (dayOf(ms) > dayOf(p.sunrise) ? ' (' + D.nextDay + ')' : ''); };
    var tn = function (i) { return i === 14 ? D.pournami : i === 29 ? D.amavasai : D.pakShort[i < 15 ? 0 : 1] + ' ' + D.tithis[i % 15]; };
    var anga = function (list, name) { return '<b>' + name(list[0].index) + '</b><small>' + D.till + ' ' + ck(list[0].end) + (list[1] ? ' · ' + D.then + ' ' + name(list[1].index) : '') + '</small>'; };
    var cell = function (k, v, cls) { return '<div class="dc ' + (cls || '') + '"><span>' + k + '</span>' + v + '</div>'; };
    var seg = function (k, s, cls, note) { return cell(k, '<b>' + clock(s.start, off) + ' – ' + clock(s.end, off) + '</b><small>' + note + '</small>', cls); };
    var tam = D.years60[p.tamil.year] + ' ' + D.varusham + ' · ' + D.months[p.tamil.month] + ' ' + p.tamil.date;
    var fest = (C.ev[sel] || []).join(' · ');
    var isToday = sel === today;
    box.innerHTML =
      '<div class="dtop"><div class="dnum">' + a[2] + '</div><div class="dwk">' + D.days[p.weekday] + (isToday ? ' · ' + D.todayL : '') + '</div>' +
      '<div class="dtam">' + tam + '</div><div class="dmon">' + C.gmonths[a[1] - 1] + ' ' + a[0] + '</div></div>' +
      '<div class="dnav"><button type="button" data-ds="-1" aria-label="' + esc(D.prevDay) + '">‹</button>' +
      '<button type="button" class="dtoday" data-ds="0">' + D.todayL + '</button>' +
      '<button type="button" data-ds="1" aria-label="' + esc(D.nextDayL) + '">›</button>' +
      '<input type="date" id="dsDate" value="' + sel + '" aria-label="' + esc(D.dateL) + '"><span class="dplace">📍 ' + esc(placeName) + '</span></div>' +
      '<div class="dbody">' + (fest ? '<p class="dfest">✨ ' + esc(fest) + '</p>' : '') +
      '<div class="dgrid">' +
      cell(D.tithi, anga(p.tithi, tn)) + cell(D.star, anga(p.nakshatra, function (i) { return D.naks[i]; })) +
      cell(D.yoga, anga(p.yoga, function (i) { return D.yogas[i]; })) + cell(D.karana, '<b>' + D.karanas[p.karana] + '</b><small>' + D.sunrise + '</small>') +
      '<div class="dc sky"><div><span>☀ ' + D.sunRS + '</span><b>' + clock(p.sunrise, off) + ' · ' + clock(p.sunset, off) + '</b></div>' +
      '<div><span>☾ ' + D.moonRS + '</span><b>' + clock(p.moonrise, off) + ' · ' + clock(p.moonset, off) + '</b>' + (!p.moonrise || !p.moonset ? '<small>— ' + D.noMoonEv + '</small>' : '') + '</div></div>' +
      seg(D.rahuKalam, p.rahu, 'avoid', D.avoid) + seg(D.yamagandam, p.yama, 'avoid', D.avoid) + seg(D.kuligai, p.gulika, 'avoid', D.avoid) + seg(D.abhijit, p.abhijit, 'good', D.goodTime) +
      '</div><a class="dwx" href="https://www.google.com/search?q=' + encodeURIComponent('weather ' + (place.name || '')) + '" target="_blank" rel="noopener">🌦 ' + esc(D.weatherL.replace('{p}', placeName)) + '</a></div>';
    mark();
  }

  // ---- the month grid: built here on the calendar home page, already on the page for a month page
  var grid = document.getElementById('mgrid');
  function buildGrid() {
    if (!grid || !C.days) return;
    var ym = sel.slice(0, 7), md = C.days.filter(function (d) { return d.d.slice(0, 7) === ym; });
    if (!md.length) { grid.innerHTML = ''; return; }
    var h = '<h2>' + C.gmonths[+ym.slice(5) - 1] + ' ' + ym.slice(0, 4) + '</h2><div class="cg-h">' + D.days.map(function (x) { return '<span>' + x.slice(0, 2) + '</span>'; }).join('') + '</div><div class="cg">' + new Array(md[0].w + 1).join('<i></i>');
    md.forEach(function (d) {
      var cls = [d.ti === 14 ? 'po' : '', d.ti === 29 ? 'am' : '', d.f ? 'fe' : '', d.w === 0 ? 'su' : '', d.d === today ? 'today' : ''].join(' ');
      h += '<a href="' + C.monthUrl + ym + '.html" class="' + cls + '" data-d="' + d.d + '"><b>' + (+d.d.slice(8)) + '</b><small>' + D.months[d.tm] + ' ' + d.td + '</small><em>' + (d.m || '') + (d.f ? '✨' : '') + '</em></a>';
    });
    grid.innerHTML = h + '</div><p class="mnav"><a href="' + C.monthUrl + ym + '.html">' + esc(D.fullMonth) + ' →</a></p>';
    grid.dataset.ym = ym;
  }
  function mark() {
    if (grid && C.days && grid.dataset.ym !== sel.slice(0, 7)) buildGrid();
    document.querySelectorAll('.cg a[data-d]').forEach(function (a) { a.classList.toggle('sel', a.getAttribute('data-d') === sel); });
  }
  function go(s, scroll) {
    sel = s; render();
    if (scroll) box.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  box.addEventListener('click', function (e) {
    var b = e.target.closest('[data-ds]'); if (!b) return;
    var n = +b.getAttribute('data-ds'); go(n === 0 ? today : shift(sel, n));
  });
  box.addEventListener('change', function (e) { if (e.target.id === 'dsDate' && e.target.value) go(e.target.value); });
  // tapping a date in the month shows that day in the sheet (instead of jumping down the page)
  document.addEventListener('click', function (e) {
    var a = e.target.closest('.cg a[data-d]'); if (!a || e.ctrlKey || e.metaKey) return;
    e.preventDefault(); e.stopPropagation(); go(a.getAttribute('data-d'), true);
  }, true);
  render();
})();
