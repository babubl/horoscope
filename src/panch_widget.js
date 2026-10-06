// Daily panchangam card used by the city pages — runs in the browser (live) and in Node (prerender at build).
(function (root) {
  'use strict';
  function fmt(s, v) { for (const k in v) s = s.split('{' + k + '}').join(v[k]); return s; }
  function clock(ms, off) { const d = new Date(Math.round((ms + off * 60000) / 60000) * 60000); return String(d.getUTCHours()).padStart(2, '0') + ':' + String(d.getUTCMinutes()).padStart(2, '0'); }
  function render(J, D, city, ymd, trad) {
    const [y, m, d] = ymd;
    const p = J.dailyPanchang({ y, m, d, lat: city.lat, lon: city.lon, zone: city.tz });
    const off = p.offset;
    const dayOf = x => Math.floor((x + off * 60000) / 86400000);
    const ck = ms => clock(ms, off) + (dayOf(ms) > dayOf(p.sunrise) ? ' (' + D.nextDay + ')' : '');
    const tn = i => i === 14 ? D.pournami : i === 29 ? D.amavasai : D.tithis[i % 15];
    const tithiTxt = i => (i === 14 || i === 29) ? tn(i) : D.pakShort[i < 15 ? 0 : 1] + ' ' + tn(i);
    const anga = (list, name) => `<b>${name(list[0].index)}</b><small>${D.till} ${ck(list[0].end)}${list[1] ? ' · ' + D.then + ' ' + name(list[1].index) : ''}</small>`;
    let cal;
    if (trad === 'ml') cal = `${fmt(D.kollamFmt, { n: p.malayalam.year })}, ${D.malMonths[p.malayalam.month]} ${p.malayalam.date}`;
    else if (trad === 'te' || trad === 'kn') { const u = p.lunar; cal = `${fmt(D.samvFmt, { name: D.years60[u.samvatsara] })}, ${u.adhika ? D.adhika + ' ' : ''}${D.lunarMonths[u.amanta]}, ${fmt(D.shakaFmt, { n: u.shaka })}`; }
    else if (trad === 'hi') { const u = p.lunar; cal = `${fmt(D.vikramFmt, { n: u.vikram })}, ${u.adhika ? D.adhika + ' ' : ''}${D.lunarMonths[u.purnimanta]}`; }
    else cal = `${D.years60[p.tamil.year]} ${D.varusham}, ${D.months[p.tamil.month]} ${p.tamil.date}`;
    const seg = (k, s, cls, note) => `<div class="pc ${cls}"><span>${k}</span><b>${ck(s.start)} – ${ck(s.end)}</b><small>${note}</small></div>`;
    const cell = (k, v) => `<div class="pc"><span>${k}</span>${v}</div>`;
    return `<div class="pgrid">
      ${cell(D['cal_' + trad], `<b>${cal}</b><small>${D.days[p.weekday]}</small>`)}
      ${cell(D.sunrise + ' / ' + D.sunset, `<b>${clock(p.sunrise, off)} · ${clock(p.sunset, off)}</b>`)}
      ${cell(D.tithi, anga(p.tithi, tithiTxt))}
      ${cell(D.star, anga(p.nakshatra, i => D.naks[i]))}
      ${cell(D.yoga, anga(p.yoga, i => D.yogas[i]))}
      ${cell(D.karana, `<b>${D.karanas[p.karana]}</b><small>${D.sunrise}</small>`)}
    </div>
    <div class="pgrid k4">
      ${seg(D.rahuKalam, p.rahu, 'avoid', D.avoid)}${seg(D.yamagandam, p.yama, 'avoid', D.avoid)}${seg(D.kuligai, p.gulika, 'avoid', D.avoid)}${seg(D.abhijit, p.abhijit, 'good', D.goodTime)}
    </div>`;
  }
  function week(J, D, city, ymd) {
    const rows = [];
    for (let i = 0; i < 7; i++) {
      const x = new Date(Date.UTC(ymd[0], ymd[1] - 1, ymd[2] + i));
      const p = J.dailyPanchang({ y: x.getUTCFullYear(), m: x.getUTCMonth() + 1, d: x.getUTCDate(), lat: city.lat, lon: city.lon, zone: city.tz });
      rows.push(`<tr><td>${String(x.getUTCDate()).padStart(2, '0')}/${String(x.getUTCMonth() + 1).padStart(2, '0')}</td><td>${D.days[p.weekday]}</td><td>${clock(p.rahu.start, p.offset)}–${clock(p.rahu.end, p.offset)}</td><td>${clock(p.yama.start, p.offset)}–${clock(p.yama.end, p.offset)}</td><td>${clock(p.gulika.start, p.offset)}–${clock(p.gulika.end, p.offset)}</td></tr>`);
    }
    return `<div class="tw"><table><tr><th></th><th>${D.weekday}</th><th>${D.rahuKalam}</th><th>${D.yamagandam}</th><th>${D.kuligai}</th></tr>${rows.join('')}</table></div>`;
  }
  function todayYMD(tz) { const p = {}; new Intl.DateTimeFormat('en-CA', { timeZone: tz, year: 'numeric', month: '2-digit', day: '2-digit' }).formatToParts(new Date()).forEach(x => p[x.type] = x.value); return [+p.year, +p.month, +p.day]; }
  const api = { render, week, todayYMD };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.SJPanch = api;
})(typeof window !== 'undefined' ? window : globalThis);
