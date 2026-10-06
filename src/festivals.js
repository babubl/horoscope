// Suba Jathagam — special-day finder. Node only (used by the site build).
// Rules: a tithi "at sunrise" (with kshaya fallback), or at sunset / midnight / moonrise / midday / afternoon;
// nakshatra days at sunrise or sunset; Tamil / Malayalam solar dates. Months are amanta (0 = Chaitra).
global.Astronomy = global.Astronomy || require('./vendor/astronomy.browser.min.js');
const J = require('./engine.js');
const A = global.Astronomy;
const DAY = 86400000;

// id, rule, regions (all = every tradition)
const EVENTS = [
  // monthly vrats
  { id: 'ekadashi_s', t: 10, at: 'sunrise', monthly: 1, reg: 'all' },
  { id: 'ekadashi_k', t: 25, at: 'sunrise', monthly: 1, reg: 'all' },
  { id: 'pradosham_s', t: 12, at: 'sunset', monthly: 1, reg: 'all' },
  { id: 'pradosham_k', t: 27, at: 'sunset', monthly: 1, reg: 'all' },
  { id: 'pournami', t: 14, at: 'sunrise', monthly: 1, reg: 'all' },
  { id: 'amavasya', t: 29, at: 'sunrise', monthly: 1, reg: 'all' },
  { id: 'sankashti', t: 18, at: 'moonrise', monthly: 1, reg: 'all' },
  { id: 'chaturthi', t: 3, at: 'midday', monthly: 1, reg: 'all' },
  { id: 'shivaratri_m', t: 28, at: 'midnight', monthly: 1, reg: 'all' },
  { id: 'shashti', t: 5, at: 'sunrise', monthly: 1, reg: 'ta' },
  { id: 'kiruthigai', nak: 2, at: 'sunrise', monthly: 1, reg: 'ta' },
  // festivals by lunar month (amanta)
  { id: 'ugadi', m: 0, t: 0, at: 'sunrise', reg: 'te kn hi' },
  { id: 'ramnavami', m: 0, t: 8, at: 'midday', reg: 'all' },
  { id: 'hanuman', m: 0, t: 14, at: 'sunrise', reg: 'hi' },
  { id: 'akshaya', m: 1, t: 2, at: 'sunrise', reg: 'all' },
  { id: 'gurupurnima', m: 3, t: 14, at: 'sunrise', reg: 'all' },
  { id: 'rakhi', m: 4, t: 14, at: 'sunrise', reg: 'all' },
  { id: 'janmashtami', m: 4, t: 22, at: 'midnight', reg: 'all' },
  { id: 'ganesh', m: 5, t: 3, at: 'midday', reg: 'all' },
  { id: 'mahalaya', m: 5, t: 29, at: 'sunrise', reg: 'all' },
  { id: 'navaratri', m: 6, t: 0, at: 'sunrise', reg: 'all' },
  { id: 'dasara', m: 6, t: 9, at: 'afternoon', reg: 'all' },
  { id: 'karva', m: 6, t: 18, at: 'moonrise', reg: 'hi' },
  { id: 'dhanteras', m: 6, t: 27, at: 'sunset', reg: 'hi' },
  { id: 'deepavali_s', m: 6, t: 28, at: 'sunrise', reg: 'ta ml te kn' },
  { id: 'diwali', m: 6, t: 29, at: 'sunset', reg: 'all' },
  { id: 'skanda', m: 7, t: 5, at: 'sunrise', reg: 'ta' },
  { id: 'vasant', m: 10, t: 4, at: 'sunrise', reg: 'hi' },
  { id: 'rathasaptami', m: 10, t: 6, at: 'sunrise', reg: 'all' },
  { id: 'mahashivaratri', m: 10, t: 28, at: 'midnight', reg: 'all' },
  { id: 'holi', m: 11, t: 15, at: 'sunrise', reg: 'hi' },
  // solar-month festivals
  { id: 'pongal', solar: 'ta', sm: 9, sd: 1, reg: 'all' },
  { id: 'puthandu', solar: 'ta', sm: 0, sd: 1, reg: 'ta' },
  { id: 'vishu', solar: 'ml', sm: 0, sd: 1, reg: 'ml' },
  { id: 'aadiperukku', solar: 'ta', sm: 3, sd: 18, reg: 'ta' },
  { id: 'aadiamavasai', solar: 'ta', sm: 3, t: 29, reg: 'ta' },
  { id: 'chithrapournami', solar: 'ta', sm: 0, t: 14, reg: 'ta' },
  { id: 'vaikasivisakam', solar: 'ta', sm: 1, nak: 15, reg: 'ta' },
  { id: 'onam', solar: 'ml', sm: 4, nak: 21, reg: 'ml' },
  { id: 'karthigaideepam', solar: 'ta', sm: 7, nak: 2, at: 'sunset', reg: 'ta' },
  { id: 'vaikunta', solar: 'ta', sm: 8, t: 10, reg: 'all' },
  { id: 'arudra', solar: 'ta', sm: 8, nak: 5, reg: 'ta' },
  { id: 'thaipusam', solar: 'ta', sm: 9, nak: 7, reg: 'ta ml' },
  { id: 'panguniuthiram', solar: 'ta', sm: 11, nak: 11, reg: 'ta' },
  // derived
  { id: 'varalakshmi', reg: 'ta te kn' },
  { id: 'holika', reg: 'hi' },
  { id: 'saraswati', reg: 'ta ml te kn' }
];

function ymdAdd(y, m, d, n) { const x = new Date(Date.UTC(y, m - 1, d + n)); return [x.getUTCFullYear(), x.getUTCMonth() + 1, x.getUTCDate()]; }
const iso = ([y, m, d]) => `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`;

function compute(city, from, to) {
  const obs = new A.Observer(city.lat, city.lon, 0);
  const days = [];
  let cur = from;
  while (iso(cur) <= iso(to)) {
    const [y, m, d] = cur;
    const p = J.dailyPanchang({ y, m, d, lat: city.lat, lon: city.lon, zone: city.tz });
    const at = t => { const f = list => (list.find(x => t < x.end) || list[list.length - 1]).index; return { t: f(p.tithi), n: f(p.nakshatra) }; };
    const mr = A.SearchRiseSet(A.Body.Moon, obs, +1, new Date(p.sunrise), 1.2);
    const midnight = J.localToUtc(...ymdAdd(y, m, d, 1), 0, 0, city.tz).utc;
    days.push({
      date: iso(cur), weekday: p.weekday, p, lunar: p.lunar, tamil: p.tamil, mal: p.malayalam,
      sunrise: at(p.sunrise + 60000), sunset: at(p.sunset), midnight: at(midnight),
      moonrise: mr ? at(mr.date.getTime()) : null, midday: at((p.sunrise + p.sunset) / 2),
      afternoon: at(p.sunrise + 0.65 * (p.sunset - p.sunrise)),
      tithis: p.tithi.filter(x => x.end <= p.nextRise + 1000 || true).map(x => x.index)
    });
    cur = ymdAdd(y, m, d, 1);
  }
  // tithi windows: start = end of the previous tithi
  const ends = new Map();
  days.forEach(D => D.p.tithi.forEach((x, i) => { const prev = i ? D.p.tithi[i - 1].end : null; ends.set(x.end, { index: x.index, start: prev, end: x.end }); }));
  const tithiWin = (D, ti) => {
    const it = D.p.tithi.find(x => x.index === ti); if (!it) return null;
    const i = D.p.tithi.indexOf(it); let start = i ? D.p.tithi[i - 1].end : null;
    if (start == null) { const k = days.indexOf(D); if (k > 0) { const pv = days[k - 1].p.tithi.find(x => x.index === ti); const pi = pv ? days[k - 1].p.tithi.indexOf(pv) : -1; if (pi > 0) start = days[k - 1].p.tithi[pi - 1].end; } }
    return { start, end: it.end };
  };
  const nakWin = (D, ni) => { const it = D.p.nakshatra.find(x => x.index === ni); if (!it) return null; const i = D.p.nakshatra.indexOf(it); let start = i ? D.p.nakshatra[i - 1].end : null;
    if (start == null) { const k = days.indexOf(D); if (k > 0) { const pv = days[k - 1].p.nakshatra; const pi = pv.findIndex(x => x.index === ni); if (pi > 0) start = pv[pi - 1].end; } } return { start, end: it.end }; };

  const out = [];
  const push = (ev, D, win) => {
    const last = out.filter(o => o.id === ev.id).pop();
    if (last && Date.parse(D.date) - Date.parse(last.date) < 5 * DAY) return; // vriddhi: keep the first day
    out.push({ id: ev.id, date: D.date, weekday: D.weekday, start: win && win.start, end: win && win.end });
  };
  const monthOk = (ev, D) => ev.m == null || (D.lunar.amanta === ev.m && !D.lunar.adhika);
  days.forEach((D, k) => {
    const N = days[k + 1];
    for (const ev of EVENTS) {
      if (ev.solar) {
        const sm = ev.solar === 'ta' ? D.tamil.month : D.mal.month;
        if (sm !== ev.sm) continue;
        if (ev.sd != null) { const sd = ev.solar === 'ta' ? D.tamil.date : D.mal.date; if (sd === ev.sd) push(ev, D, null); continue; }
        if (ev.nak != null) { const when = ev.at === 'sunset' ? D.sunset : D.sunrise; if (when.n === ev.nak) push(ev, D, nakWin(D, ev.nak)); continue; }
        if (ev.t != null) { if (D.sunrise.t === ev.t || (D.tithis.includes(ev.t) && N && N.sunrise.t !== ev.t && D.sunrise.t !== ev.t)) push(ev, D, tithiWin(D, ev.t)); continue; }
      }
      if (ev.nak != null && !ev.solar) { if (D.sunrise.n === ev.nak) push(ev, D, nakWin(D, ev.nak)); continue; }
      if (ev.t == null) continue;
      const atv = ev.at === 'sunrise' ? D.sunrise : D[ev.at];
      if (atv && atv.t === ev.t && monthOk(ev, D)) { push(ev, D, tithiWin(D, ev.t)); continue; }
      // kshaya: the tithi starts and ends between two sunrises
      if (ev.at === 'sunrise' && D.tithis.includes(ev.t) && D.sunrise.t !== ev.t && N && N.sunrise.t !== ev.t && (monthOk(ev, D) || monthOk(ev, N))) push(ev, D, tithiWin(D, ev.t));
    }
  });
  // second pass for rules that missed (moonrise/midnight/sunset with no hit in a lunation): fall back to the sunrise day
  // derived events
  out.filter(o => o.id === 'rakhi').forEach(r => {
    let [y, m, d] = r.date.split('-').map(Number);
    for (let i = 1; i <= 7; i++) { const [a, b, c] = ymdAdd(y, m, d, -i); if (new Date(Date.UTC(a, b - 1, c)).getUTCDay() === 5) { out.push({ id: 'varalakshmi', date: iso([a, b, c]), weekday: 5 }); break; } }
  });
  const dayBefore = (src, id) => out.filter(o => o.id === src).forEach(r => {
    const [y, m, d] = r.date.split('-').map(Number), n = ymdAdd(y, m, d, -1);
    out.push({ id, date: iso(n), weekday: new Date(Date.UTC(n[0], n[1] - 1, n[2])).getUTCDay() });
  });
  dayBefore('holi', 'holika'); dayBefore('dasara', 'saraswati');
  out.sort((a, b) => a.date.localeCompare(b.date) || a.id.localeCompare(b.id));
  return out;
}
module.exports = { EVENTS, compute };
if (require.main === module) {
  const city = JSON.parse(process.argv[2]);
  process.stdout.write(JSON.stringify(compute(city, JSON.parse(process.argv[3]), JSON.parse(process.argv[4]))));
}
