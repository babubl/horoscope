/* Jothidam engine — South Indian Vedic calculations (Lahiri ayanamsa, whole-sign houses)
   Works in the browser (global Astronomy) and in Node (require('astronomy-engine')). */
(function (root) {
  const A = (typeof Astronomy !== 'undefined') ? Astronomy : require('astronomy-engine');
  const norm = x => ((x % 360) + 360) % 360;
  const D2R = Math.PI / 180, R2D = 180 / Math.PI;

  // ---------- reference data ----------
  const PLANETS = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu'];
  const RASI_LORD = ['Mars', 'Venus', 'Mercury', 'Moon', 'Sun', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Saturn', 'Jupiter'];
  const DASA_LORDS = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury'];
  const DASA_YEARS = { Ketu: 7, Venus: 20, Sun: 6, Moon: 10, Mars: 7, Rahu: 18, Jupiter: 16, Saturn: 19, Mercury: 17 };
  const EXALT = { Sun: 0, Moon: 1, Mars: 9, Mercury: 5, Jupiter: 3, Venus: 11, Saturn: 6, Rahu: 1, Ketu: 7 };
  const DEBIL = { Sun: 6, Moon: 7, Mars: 3, Mercury: 11, Jupiter: 9, Venus: 5, Saturn: 0, Rahu: 7, Ketu: 1 };
  const OWN = { Sun: [4], Moon: [3], Mars: [0, 7], Mercury: [2, 5], Jupiter: [8, 11], Venus: [1, 6], Saturn: [9, 10], Rahu: [], Ketu: [] };

  // ---------- time helpers ----------
  // Offset (minutes) of an IANA zone at a given UTC instant, using the browser/Node tz database.
  function tzOffsetMinutes(zone, utcMs) {
    const f = new Intl.DateTimeFormat('en-US', { timeZone: zone, hourCycle: 'h23', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const p = {}; f.formatToParts(new Date(utcMs)).forEach(x => p[x.type] = x.value);
    const asUtc = Date.UTC(+p.year, +p.month - 1, +p.day, +p.hour % 24, +p.minute, +p.second);
    return Math.round((asUtc - utcMs) / 60000);
  }
  // Local wall time (y,m,d,h,mi) in zone -> UTC ms. Offset in minutes may be given directly instead.
  function localToUtc(y, m, d, h, mi, zoneOrOffset) {
    const wall = Date.UTC(y, m - 1, d, h, mi);
    if (typeof zoneOrOffset === 'number') return { utc: wall - zoneOrOffset * 60000, offset: zoneOrOffset };
    let off = tzOffsetMinutes(zoneOrOffset, wall);
    let utc = wall - off * 60000;
    const off2 = tzOffsetMinutes(zoneOrOffset, utc);
    if (off2 !== off) { off = off2; utc = wall - off * 60000; }
    return { utc, offset: off };
  }

  // ---------- astronomy ----------
  function julianCenturies(date) { return (date.getTime() / 86400000 + 2440587.5 - 2451545.0) / 36525; }

  // Lahiri (Chitrapaksha) ayanamsa — anchored to 23°51'25" at J2000 with IAU precession rate.
  function ayanamsa(date) {
    const T = julianCenturies(date);
    return 23.85694 + (5028.796195 * T + 1.1054348 * T * T) / 3600;
  }
  function meanObliquity(date) {
    const T = julianCenturies(date);
    return 23.439291 - 0.0130042 * T - 1.64e-7 * T * T + 5.04e-7 * T * T * T;
  }
  function meanNode(date) {
    const T = julianCenturies(date);
    return norm(125.0445479 - 1934.1362891 * T + 0.0020754 * T * T + T * T * T / 467441);
  }
  function trueNode(t) {
    const st = A.GeoMoonState(t);
    const r = A.Ecliptic(new A.Vector(st.x, st.y, st.z, t)).vec;
    const v = A.Ecliptic(new A.Vector(st.vx, st.vy, st.vz, t)).vec;
    const hx = r.y * v.z - r.z * v.y, hy = r.z * v.x - r.x * v.z;
    return norm(Math.atan2(hx, -hy) * R2D);
  }
  function tropicalLongitudes(date, nodeType) {
    const t = A.MakeTime(date);
    const out = {};
    out.Sun = A.SunPosition(t).elon;
    out.Moon = A.EclipticGeoMoon(t).lon;
    const map = { Mars: A.Body.Mars, Mercury: A.Body.Mercury, Jupiter: A.Body.Jupiter, Venus: A.Body.Venus, Saturn: A.Body.Saturn };
    for (const k in map) out[k] = A.Ecliptic(A.GeoVector(map[k], t, true)).elon;
    out.Rahu = nodeType === 'true' ? trueNode(t) : meanNode(date);
    out.Ketu = norm(out.Rahu + 180);
    // Convert from true equinox of date to mean equinox (removes nutation), matching Swiss Ephemeris / Drik sidereal positions
    const dpsi = A.e_tilt(t).dpsi / 3600;
    for (const k in out) if (k !== 'Rahu' && k !== 'Ketu' || nodeType === 'true') out[k] = norm(out[k] - dpsi);
    return out;
  }
  function ascendantTropical(date, lat, lon) {
    const t = A.MakeTime(date), tilt = A.e_tilt(t);
    const gast = A.SiderealTime(t); // hours, apparent
    const ramc = norm(gast * 15 + lon) * D2R;
    const eps = tilt.tobl * D2R, phi = lat * D2R;
    const asc = Math.atan2(Math.cos(ramc), -(Math.sin(ramc) * Math.cos(eps) + Math.tan(phi) * Math.sin(eps)));
    return norm(asc * R2D - tilt.dpsi / 3600);
  }

  // ---------- chart ----------
  function dignity(p, sign) {
    if (EXALT[p] === sign) return 'exalted';
    if (DEBIL[p] === sign) return 'debilitated';
    if (OWN[p].includes(sign)) return 'own';
    return '';
  }
  function navamsaSign(lon) { return Math.floor(lon / (30 / 9)) % 12; }
  function nakInfo(lon) {
    const span = 360 / 27;
    const idx = Math.floor(lon / span);
    const within = lon - idx * span;
    return { index: idx, pada: Math.floor(within / (span / 4)) + 1, fraction: within / span };
  }

  function computeChart({ y, m, d, h, mi, lat, lon, zone, offsetMinutes, nodeType }) {
    nodeType = nodeType === 'true' ? 'true' : 'mean';
    const { utc, offset } = localToUtc(y, m, d, h, mi, offsetMinutes != null ? offsetMinutes : zone);
    const date = new Date(utc);
    const ay = ayanamsa(date);
    const trop = tropicalLongitudes(date, nodeType);
    const tropNext = tropicalLongitudes(new Date(utc + 86400000), nodeType);
    const ascSid = norm(ascendantTropical(date, lat, lon) - ay);
    const lagnaSign = Math.floor(ascSid / 30);

    const planets = PLANETS.map(p => {
      const L = norm(trop[p] - ay);
      const sign = Math.floor(L / 30);
      let delta = norm(tropNext[p] - trop[p]); if (delta > 180) delta -= 360;
      const retro = (p === 'Rahu' || p === 'Ketu') ? true : (p !== 'Sun' && p !== 'Moon' && delta < 0);
      const nk = nakInfo(L);
      return {
        name: p, lon: L, sign, deg: L - sign * 30, house: ((sign - lagnaSign + 12) % 12) + 1,
        nakshatra: nk.index, pada: nk.pada, navamsa: navamsaSign(L), retro, dignity: dignity(p, sign)
      };
    });
    const P = Object.fromEntries(planets.map(p => [p.name, p]));
    const lagnaNk = nakInfo(ascSid);
    const lagna = { lon: ascSid, sign: lagnaSign, deg: ascSid - lagnaSign * 30, nakshatra: lagnaNk.index, pada: lagnaNk.pada, navamsa: navamsaSign(ascSid) };

    // Combustion (within classical orbs of the Sun)
    const ORB = { Moon: 12, Mars: 17, Mercury: 14, Jupiter: 11, Venus: 10, Saturn: 15 };
    planets.forEach(p => {
      if (ORB[p.name]) { let dd = Math.abs(p.lon - P.Sun.lon); if (dd > 180) dd = 360 - dd; p.combust = dd < ORB[p.name]; }
    });

    const moon = P.Moon, sun = P.Sun;
    const nk = nakInfo(moon.lon);
    const dasa = vimshottari(nk, utc);
    const panchang = panchanga(sun.lon, moon.lon, y, m, d);
    const tamil = tamilCalendar(utc, offset, lat, lon);
    panchang.weekday = tamil.weekday;
    const doshas = doshaChecks(P, lagna);

    return {
      input: { y, m, d, h, mi, lat, lon, zone, offsetMinutes: offset }, utc, ayanamsa: ay,
      lagna, planets, rasi: moon.sign, nakshatra: nk.index, pada: nk.pada,
      tamilMonth: tamil.month, tamil, nodeType, dasa, panchang, doshas
    };
  }

  // ---------- Vimshottari dasa ----------
  const YEAR_MS = 365.25 * 86400000;
  function vimshottari(nk, birthUtc) {
    const startLordIdx = nk.index % 9;
    const lord0 = DASA_LORDS[startLordIdx];
    const balanceYears = DASA_YEARS[lord0] * (1 - nk.fraction);
    // Start of the first mahadasa (theoretical, before birth)
    let t = birthUtc - (DASA_YEARS[lord0] - balanceYears) * YEAR_MS;
    const periods = [];
    for (let i = 0; i < 18; i++) { // two full cycles covers any lifetime
      const lord = DASA_LORDS[(startLordIdx + i) % 9];
      const len = DASA_YEARS[lord] * YEAR_MS;
      const md = { lord, start: t, end: t + len, bhuktis: [] };
      let bt = t;
      for (let j = 0; j < 9; j++) {
        const bl = DASA_LORDS[(DASA_LORDS.indexOf(lord) + j) % 9];
        const blen = DASA_YEARS[lord] * DASA_YEARS[bl] / 120 * YEAR_MS;
        md.bhuktis.push({ lord: bl, start: bt, end: bt + blen });
        bt += blen;
      }
      periods.push(md);
      t += len;
      if (t > birthUtc + 120 * YEAR_MS) break;
    }
    return { balance: { lord: lord0, years: balanceYears }, periods };
  }
  function currentDasa(dasa, atMs) {
    const md = dasa.periods.find(p => atMs >= p.start && atMs < p.end);
    if (!md) return null;
    const bh = md.bhuktis.find(b => atMs >= b.start && atMs < b.end);
    return { md, bh };
  }

  // ---------- Panchangam ----------
  function panchanga(sunL, moonL, y, m, d) {
    const diff = norm(moonL - sunL);
    const tithi = Math.floor(diff / 12); // 0..29
    const yoga = Math.floor(norm(sunL + moonL) / (360 / 27));
    const k = Math.floor(diff / 6); // 0..59
    let karana;
    if (k === 0) karana = 10; else if (k >= 57) karana = 7 + (k - 57); else karana = (k - 1) % 7;
    const weekday = new Date(Date.UTC(y, m - 1, d)).getUTCDay();
    return { tithi, paksha: tithi < 15 ? 'shukla' : 'krishna', yoga, karana, weekday };
  }


  // ---------- Tamil calendar (sunrise-based day, sankranti-before-sunset rule) ----------
  function siderealSun(ms) {
    const d = new Date(ms), t = A.MakeTime(d);
    return norm(A.SunPosition(t).elon - A.e_tilt(t).dpsi / 3600 - ayanamsa(d));
  }
  function tamilCalendar(utc, offset, lat, lon) {
    const obs = new A.Observer(lat, lon, 0), DAY = 86400000;
    const localMidnight = ms => { const l = ms + offset * 60000; return l - (((l % DAY) + DAY) % DAY) - offset * 60000; };
    const riseSet = (dir, fromMs) => { const r = A.SearchRiseSet(A.Body.Sun, obs, dir, new Date(fromMs), 1.2); return r ? r.date.getTime() : null; };
    let d0 = localMidnight(utc);
    let rise = riseSet(+1, d0);
    let beforeSunrise = false;
    if (rise != null && utc < rise) { beforeSunrise = true; d0 -= DAY; rise = riseSet(+1, d0); }
    const sunriseOk = rise != null;
    if (!sunriseOk) rise = d0 + 6 * 3600000; // polar fallback
    const set = riseSet(-1, rise) ?? (d0 + 18 * 3600000);
    // Tamil month = Sun's sign at sunset of the Tamil day
    const month = Math.floor(siderealSun(set) / 30);
    let a = set, b;
    for (let i = 0; i < 40; i++) { b = a; a -= DAY; if (Math.floor(siderealSun(a) / 30) !== month) break; }
    for (let i = 0; i < 40; i++) { const mid = (a + b) / 2; if (Math.floor(siderealSun(mid) / 30) === month) b = mid; else a = mid; }
    const sankranti = b;
    let start = localMidnight(sankranti);
    const ssOnStart = riseSet(-1, start + 3 * 3600000) ?? (start + 18 * 3600000);
    if (sankranti > ssOnStart) start += DAY;
    const date = Math.round((d0 - start) / DAY) + 1;
    const loc = new Date(d0 + offset * 60000 + 12 * 3600000);
    let gy = loc.getUTCFullYear();
    if (loc.getUTCMonth() + 1 <= 4 && month >= 8) gy -= 1;
    const year = (((gy - 1987) % 60) + 60) % 60;
    const naz = (utc - rise) / 60000 / 24;
    return {
      year, month, date, weekday: loc.getUTCDay(), sunrise: rise, sunset: set, sunriseOk, beforeSunrise,
      nazhigai: Math.floor(naz), vinadi: Math.floor((naz - Math.floor(naz)) * 60), sankranti
    };
  }

  // ---------- Current transits (Gochara) from the Moon sign ----------
  function transits(chart, atMs) {
    const d = new Date(atMs), ay = ayanamsa(d), trop = tropicalLongitudes(d, chart.nodeType);
    return ['Saturn', 'Jupiter', 'Rahu', 'Ketu'].map(p => {
      const L = norm(trop[p] - ay), sign = Math.floor(L / 30);
      return { name: p, sign, fromMoon: ((sign - chart.rasi + 12) % 12) + 1, fromLagna: ((sign - chart.lagna.sign + 12) % 12) + 1 };
    });
  }
  function saturnPhase(fromMoon) {
    if ([12, 1, 2].includes(fromMoon)) return { key: 'sadeSati', part: fromMoon === 12 ? 1 : fromMoon === 1 ? 2 : 3 };
    if (fromMoon === 8) return { key: 'ashtama' };
    if (fromMoon === 4) return { key: 'ardhashtama' };
    if (fromMoon === 7) return { key: 'kandaka' };
    return null;
  }

  // ---------- Doshas ----------
  function doshaChecks(P, lagna) {
    const mars = P.Mars;
    const fromLagna = ((mars.sign - lagna.sign + 12) % 12) + 1;
    const fromMoon = ((mars.sign - P.Moon.sign + 12) % 12) + 1;
    const BAD = [2, 4, 7, 8, 12];
    // Classical cancellations by Mars' sign for each house
    const CANCEL = { 2: [2, 5], 4: [0, 7], 7: [3, 9], 8: [8, 11], 12: [1, 6] };
    const cancelledBy = h => mars.dignity === 'own' || mars.dignity === 'exalted' || (CANCEL[h] || []).includes(mars.sign);
    const refs = [['lagna', fromLagna], ['moon', fromMoon]].filter(r => BAD.includes(r[1]));
    const active = refs.filter(r => !cancelledBy(r[1]));
    const chevvai = { present: refs.length > 0, effective: active.length > 0, refs: refs.map(r => ({ from: r[0], house: r[1], cancelled: cancelledBy(r[1]) })) };

    const rahuH = P.Rahu.house, ketuH = P.Ketu.house;
    const rk = [1, 2, 7, 8];
    const rahuKetu = { present: rk.includes(rahuH) || rk.includes(ketuH), rahuHouse: rahuH, ketuHouse: ketuH };

    // Kala Sarpa: all seven planets on one side of the Rahu–Ketu axis
    const side = p => norm(P[p].lon - P.Rahu.lon) < 180;
    const seven = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn'];
    const s = seven.map(side);
    const kalaSarpa = s.every(x => x) || s.every(x => !x);
    return { chevvai, rahuKetu, kalaSarpa };
  }

  // ---------- 10 Porutham ----------
  const GANA = [0, 1, 2, 1, 0, 1, 0, 0, 2, 2, 1, 1, 0, 2, 0, 2, 0, 2, 2, 1, 1, 0, 2, 2, 1, 1, 0]; // 0 Deva 1 Manushya 2 Rakshasa
  // Yoni animal ids: 0 Horse 1 Elephant 2 Goat 3 Serpent 4 Dog 5 Cat 6 Rat 7 Cow 8 Buffalo 9 Tiger 10 Deer 11 Monkey 12 Mongoose 13 Lion
  const YONI = [[0, 'M'], [1, 'M'], [2, 'F'], [3, 'M'], [3, 'F'], [4, 'F'], [5, 'F'], [2, 'M'], [5, 'M'], [6, 'M'], [6, 'F'], [7, 'M'], [8, 'F'], [9, 'F'], [8, 'M'], [9, 'M'], [10, 'F'], [10, 'M'], [4, 'M'], [11, 'M'], [12, 'M'], [11, 'F'], [13, 'F'], [0, 'F'], [13, 'M'], [7, 'F'], [1, 'F']];
  const YONI_ENEMY = [[0, 8], [1, 13], [2, 11], [3, 12], [4, 10], [5, 6], [7, 9]];
  // Rajju: 0 Siro(head) 1 Kanta(neck) 2 Udara(navel) 3 Kati(waist) 4 Pada(feet)
  const RAJJU = [4, 3, 2, 1, 0, 1, 2, 3, 4, 4, 3, 2, 1, 0, 1, 2, 3, 4, 4, 3, 2, 1, 0, 1, 2, 3, 4];
  const VEDHA = [[0, 17], [1, 16], [2, 15], [3, 14], [5, 21], [6, 20], [7, 19], [8, 18], [9, 26], [10, 25], [11, 24], [12, 23], [4, 22], [22, 13], [4, 13]];
  const VASYA = { 0: [4, 7], 1: [3, 6], 2: [5], 3: [7, 8], 4: [9], 5: [1, 11], 6: [9], 7: [3, 5], 8: [11], 9: [10], 10: [11], 11: [9] }; // girl's rasi -> boy's rasi (Tamil list)
  const FRIENDS = {
    Sun: { f: ['Moon', 'Mars', 'Jupiter'], e: ['Venus', 'Saturn'] },
    Moon: { f: ['Sun', 'Mercury'], e: [] },
    Mars: { f: ['Sun', 'Moon', 'Jupiter'], e: ['Mercury'] },
    Mercury: { f: ['Sun', 'Venus'], e: ['Moon'] },
    Jupiter: { f: ['Sun', 'Moon', 'Mars'], e: ['Mercury', 'Venus'] },
    Venus: { f: ['Mercury', 'Saturn'], e: ['Sun', 'Moon'] },
    Saturn: { f: ['Mercury', 'Venus'], e: ['Sun', 'Moon', 'Mars'] }
  };
  const rel = (a, b) => FRIENDS[a].f.includes(b) ? 'friend' : FRIENDS[a].e.includes(b) ? 'enemy' : 'neutral';
  const SAME_STAR_GOOD = [3, 5, 7, 9, 12, 21]; // Rohini, Thiruvathirai, Poosam, Magam, Hastham, Thiruvonam
  const EKA_RASI_OK = [0, 2, 3, 9, 12, 14, 19, 23]; // same-rasi stars acceptable either order

  // result codes: 'good' (1), 'medium' (0.5), 'bad' (0)
  function porutham(girl, boy) {
    const gs = girl.nakshatra, bs = boy.nakshatra, gr = girl.rasi, br = boy.rasi;
    const n = ((bs - gs + 27) % 27) + 1;      // count girl → boy star (inclusive)
    const r = ((br - gr + 12) % 12) + 1;      // count girl → boy rasi (inclusive)
    const res = [];

    // 1 Dinam — good counts 2,4,6,8,9,11,13,15,18,20,24,26; 12/14/16 average except one pada; 27 rejected
    let dina;
    const bp = boy.pada || 0;
    if (n === 1) dina = SAME_STAR_GOOD.includes(gs) ? 'good' : 'medium';
    else if ([2, 4, 6, 8, 9, 11, 13, 15, 18, 20, 24, 26].includes(n)) dina = 'good';
    else if ((n === 12 && bp !== 1) || (n === 14 && bp !== 4) || (n === 16 && bp !== 3)) dina = 'medium';
    else dina = 'bad';
    res.push({ key: 'dinam', result: dina, detail: { count: n } });

    // 2 Ganam
    const gg = GANA[gs], bg = GANA[bs];
    let gana;
    if (gg === bg) gana = 'good';                 // same gana
    else if (bg === 2) gana = 'bad';               // boy Rakshasa, girl Deva/Manushya
    else gana = 'medium';                          // Deva–Manushya either way, or girl Rakshasa
    res.push({ key: 'ganam', result: gana, detail: { girl: gg, boy: bg } });

    // 3 Mahendram
    res.push({ key: 'mahendram', result: [4, 7, 10, 13, 16, 19, 22, 25].includes(n) ? 'good' : 'bad', detail: { count: n } });

    // 4 Stree Deergham
    res.push({ key: 'streeDeergham', result: n > 13 ? 'good' : n > 7 ? 'medium' : 'bad', detail: { count: n } });

    // 5 Yoni
    const [ga, gsx] = YONI[gs], [ba, bsx] = YONI[bs];
    const enemy = YONI_ENEMY.some(([x, y]) => (x === ga && y === ba) || (x === ba && y === ga));
    let yoni;
    if (enemy) yoni = 'bad';
    else if (ga === ba) yoni = (gsx !== bsx) ? 'good' : 'medium';
    else yoni = (bsx === 'M' && gsx === 'F') ? 'good' : 'medium';
    res.push({ key: 'yoni', result: yoni, detail: { girl: ga, boy: ba, enemy } });

    // 6 Rasi — 7th best; 3,4,5,9,10,11 good; 2,6,8,12 not matching; same rasi good if boy's star is ahead
    let rasi;
    if ([2, 6, 8, 12].includes(r)) rasi = 'bad';
    else if (r === 1) rasi = gs === bs ? 'medium' : (bs > gs || EKA_RASI_OK.includes(gs) ? 'good' : 'bad');
    else rasi = 'good';
    res.push({ key: 'rasi', result: rasi, detail: { count: r } });

    // 7 Rasi Adhipathi
    const gl = RASI_LORD[gr], bl = RASI_LORD[br];
    let adh;
    if (gl === bl) adh = 'good';
    else {
      const a = rel(gl, bl), b = rel(bl, gl);
      if (a === 'enemy' || b === 'enemy') adh = 'bad';
      else if (a === 'friend' && b === 'friend') adh = 'good';
      else adh = 'medium';
    }
    res.push({ key: 'rasiAdhipathi', result: adh, detail: { girl: gl, boy: bl } });

    // 8 Vasyam — boy's rasi vasya to girl's: good; only the reverse: average
    const vas = (VASYA[gr] || []).includes(br) ? 'good' : (VASYA[br] || []).includes(gr) ? 'medium' : 'bad';
    res.push({ key: 'vasyam', result: vas, detail: {} });

    // 9 Rajju
    const rajjuBad = RAJJU[gs] === RAJJU[bs];
    res.push({ key: 'rajju', result: rajjuBad ? 'bad' : 'good', detail: { girl: RAJJU[gs], boy: RAJJU[bs] }, critical: true });

    // 10 Vedhai
    const vedhaBad = VEDHA.some(([x, y]) => (x === gs && y === bs) || (x === bs && y === gs));
    res.push({ key: 'vedhai', result: vedhaBad ? 'bad' : 'good', detail: {}, critical: true });

    const score = res.reduce((s, x) => s + (x.result === 'good' ? 1 : x.result === 'medium' ? 0.5 : 0), 0);
    const criticalFail = rajjuBad || vedhaBad;
    let verdict;
    if (criticalFail) verdict = 'notRecommended';
    else if (score >= 7) verdict = 'excellent';
    else if (score >= 5.5) verdict = 'good';
    else if (score >= 4) verdict = 'average';
    else verdict = 'weak';
    return { items: res, score, verdict, criticalFail };
  }

  function doshaCompat(girlChart, boyChart) {
    const g = girlChart.doshas.chevvai.effective, b = boyChart.doshas.chevvai.effective;
    const gr = girlChart.doshas.rahuKetu.present, br = boyChart.doshas.rahuKetu.present;
    return { chevvai: { girl: g, boy: b, balanced: g === b }, rahuKetu: { girl: gr, boy: br, balanced: gr === br } };
  }

  const api = { computeChart, currentDasa, transits, saturnPhase, porutham, doshaCompat, localToUtc, tzOffsetMinutes, ayanamsa, RASI_LORD, DASA_YEARS, GANA, YONI, RAJJU, PLANETS };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.Jothidam = api;
})(typeof window !== 'undefined' ? window : globalThis);
