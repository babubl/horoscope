/* Suba Jathagam — temple ambience (soft drone, veena and far-off bells, synthesised in the browser, no audio files),
   the "light a lamp" diya and the "open now" badge on temple pages.
   Sound never starts by itself: the visitor taps the bell. The choice is remembered on this device,
   and resumes on the next tap anywhere if they left it on. Not shown inside the Android app. */
(function () {
  var app = false;
  try { app = sessionStorage.getItem('jothidam.app') === '1' || /[?&]source=twa\b/.test(location.search); } catch (e) {}
  var KEY = 'sj.music';
  var ctx = null, master = null, droneNodes = null, bellTimer = null, playing = false;
  var tamil = document.documentElement.lang === 'ta';
  var T = tamil ? { on: 'இசையை நிறுத்த', off: 'தெய்வீக இசை கேட்க' } : { on: 'Stop the music', off: 'Play soft divine music' };

  function ac() {
    if (!ctx) {
      var C = window.AudioContext || window.webkitAudioContext;
      if (!C) return null;
      ctx = new C();
      master = ctx.createGain();
      master.gain.value = 0.0001;
      var comp = ctx.createDynamicsCompressor();
      master.connect(comp); comp.connect(ctx.destination);
    }
    if (ctx.state === 'suspended') ctx.resume();
    return ctx;
  }

  // A temple bell: inharmonic partials with long, different decays, plus a short metallic strike.
  function bell(pitch, vol) {
    var c = ac(); if (!c) return;
    var t0 = c.currentTime + 0.02;
    pitch = pitch || 440; vol = vol || 0.32;
    var out = c.createGain(); out.gain.value = vol; out.connect(master || c.destination);
    var P = [[0.5, 0.55, 6], [1, 1, 4.5], [1.183, 0.5, 3.4], [1.506, 0.42, 2.6], [2, 0.38, 2.1], [2.514, 0.25, 1.6], [2.662, 0.2, 1.4], [3.011, 0.14, 1.1], [4.166, 0.09, 0.7], [5.433, 0.05, 0.45]];
    P.forEach(function (p) {
      var o = c.createOscillator(), g = c.createGain();
      o.type = 'sine';
      o.frequency.value = pitch * p[0];
      o.detune.value = (Math.random() - 0.5) * 7;
      g.gain.setValueAtTime(0.0001, t0);
      g.gain.exponentialRampToValueAtTime(p[1], t0 + 0.005);
      g.gain.exponentialRampToValueAtTime(0.0001, t0 + p[2]);
      o.connect(g); g.connect(out);
      o.start(t0); o.stop(t0 + p[2] + 0.05);
    });
    // strike: a burst of filtered noise
    var n = c.createBufferSource(), buf = c.createBuffer(1, Math.floor(c.sampleRate * 0.05), c.sampleRate), d = buf.getChannelData(0);
    for (var i = 0; i < d.length; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / d.length, 3);
    n.buffer = buf;
    var bp = c.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.value = pitch * 6; bp.Q.value = 2;
    var ng = c.createGain(); ng.gain.value = 0.25;
    n.connect(bp); bp.connect(ng); ng.connect(out); n.start(t0);
  }

  // ---- Divine music: a soft, slowly breathing drone, a veena playing slow phrases in raga Mohanam and,
  // now and then, a small temple bell far away. All synthesised here with a warm hall reverb: nothing is
  // downloaded and nothing is copyrighted. Kept quiet on purpose — it should be felt more than heard.
  var SA = 138.6, reverb = null, timers = [], pad = [], ks = {};
  function hall() {
    if (reverb) return reverb;
    var c = ctx, len = Math.floor(c.sampleRate * 4.5), buf = c.createBuffer(2, len, c.sampleRate);
    for (var ch = 0; ch < 2; ch++) {
      var d = buf.getChannelData(ch), lp = 0;
      for (var i = 0; i < len; i++) { lp += 0.35 * ((Math.random() * 2 - 1) - lp); d[i] = lp * Math.pow(1 - i / len, 3); } // darker, softer tail
    }
    reverb = c.createConvolver(); reverb.buffer = buf;
    var wet = c.createGain(); wet.gain.value = 0.7; reverb.connect(wet); wet.connect(master);
    return reverb;
  }
  function voice(dry) { var g = ctx.createGain(); g.connect(hall()); var d = ctx.createGain(); d.gain.value = dry; g.connect(d); d.connect(master); return g; }

  // the drone: pure sine tones on Sa, Pa and upper Sa that swell and fade very slowly, like breath
  function padStart() {
    var t = ctx.currentTime, lp = ctx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 900; lp.connect(voice(0.6));
    [[SA, 0.05, 0.07], [SA * 1.5, 0.025, 0.05], [SA * 2, 0.03, 0.09], [SA * 2.003, 0.02, 0.11]].forEach(function (v) {
      var o = ctx.createOscillator(), g = ctx.createGain(), lfo = ctx.createOscillator(), lg = ctx.createGain();
      o.type = 'sine'; o.frequency.value = v[0];
      g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(v[1], t + 6);
      lfo.frequency.value = v[2]; lg.gain.value = v[1] * 0.45; lfo.connect(lg); lg.connect(g.gain);
      o.connect(g); g.connect(lp); o.start(t); lfo.start(t);
      pad.push(o, lfo);
    });
  }
  function padStop() { var t = ctx.currentTime + 1.5; pad.forEach(function (o) { try { o.stop(t); } catch (e) {} }); pad = []; }

  // a veena string (Karplus–Strong): a soft pluck that rings and mellows, played back at the note's pitch
  function veenaBuf(f) {
    if (ks[f]) return ks[f];
    var sr = ctx.sampleRate, N = Math.max(2, Math.round(sr / f)), len = Math.floor(sr * 4.2), buf = ctx.createBuffer(1, len, sr), d = buf.getChannelData(0);
    var ring = new Float32Array(N), i, k = 0, mx = 0;
    for (i = 0; i < N; i++) ring[i] = Math.random() * 2 - 1;
    for (var pass = 0; pass < 3; pass++) for (i = 1; i < N; i++) ring[i] = 0.5 * (ring[i] + ring[i - 1]); // a finger, not a pick: soft attack
    for (i = 0; i < len; i++) {
      var a = ring[k], b = ring[(k + 1) % N];
      d[i] = a; ring[k] = 0.4992 * (a + b);
      k = (k + 1) % N;
      if (Math.abs(a) > mx) mx = Math.abs(a);
    }
    var fade = Math.floor(sr * 0.6);
    for (i = 0; i < len; i++) { d[i] /= mx || 1; if (i > len - fade) d[i] *= (len - i) / fade; }
    return (ks[f] = buf);
  }
  var body = null;
  function veena(ratio, t, vol, gamaka) {
    if (!body) {
      var lp = ctx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 2400; lp.Q.value = 0.4;
      var pk = ctx.createBiquadFilter(); pk.type = 'peaking'; pk.frequency.value = 280; pk.gain.value = 4; pk.Q.value = 0.8;
      lp.connect(pk); pk.connect(voice(0.55)); body = lp;
    }
    var src = ctx.createBufferSource(), g = ctx.createGain();
    src.buffer = veenaBuf(SA * 2); // one tuned string, stopped at each note by changing the playback rate
    var r = src.playbackRate;
    if (gamaka === 'slide') { r.setValueAtTime(ratio * 0.944, t); r.linearRampToValueAtTime(ratio, t + 0.22); }       // glide up into the note
    else if (gamaka === 'shake') { r.setValueAtTime(ratio, t); for (var q = 0; q < 3; q++) { r.linearRampToValueAtTime(ratio * 1.03, t + 0.25 + q * 0.36); r.linearRampToValueAtTime(ratio, t + 0.43 + q * 0.36); } } // a gentle kampitam
    else r.setValueAtTime(ratio, t);
    g.gain.value = vol;
    src.connect(g); g.connect(body); src.start(t); src.stop(t + 4.2);
  }
  // a small, far-off temple bell: only the pure partials, no strike, deep in the reverb
  function softBell(pitch, vol) {
    var t0 = ctx.currentTime + 0.05, out = voice(0.25); var og = ctx.createGain(); og.gain.value = vol; og.connect(out);
    [[1, 1, 5], [2.01, 0.35, 3.5], [2.76, 0.18, 2.4], [5.4, 0.06, 1.2]].forEach(function (p) {
      var o = ctx.createOscillator(), g = ctx.createGain(); o.type = 'sine'; o.frequency.value = pitch * p[0];
      g.gain.setValueAtTime(0.0001, t0); g.gain.exponentialRampToValueAtTime(p[1], t0 + 0.03); g.gain.exponentialRampToValueAtTime(0.0001, t0 + p[2]);
      o.connect(g); g.connect(og); o.start(t0); o.stop(t0 + p[2] + 0.1);
    });
  }
  function bells() {
    if (!playing) return;
    softBell(SA * 8, 0.05); if (Math.random() < 0.5) timers.push(setTimeout(function () { if (playing) softBell(SA * 12, 0.03); }, 1400));
    timers.push(setTimeout(bells, 22000 + Math.random() * 20000));
  }
  // Mohanam: Sa Ri2 Ga3 Pa Da2 — slow phrases that move a step at a time and rest on Sa, Ga or Pa
  var SCALE = [0.75, 5 / 6, 1, 9 / 8, 5 / 4, 3 / 2, 5 / 3, 2];
  var pos = 2;
  function phrase() {
    if (!playing) return;
    var t = ctx.currentTime + 0.1, n = 3 + Math.floor(Math.random() * 4);
    for (var i = 0; i < n; i++) {
      var step = [-1, -1, 1, 1, 2, -2, 0][Math.floor(Math.random() * 7)];
      pos = Math.max(0, Math.min(SCALE.length - 1, pos + step));
      if (i === n - 1) pos = [2, 4, 5, 7][Math.floor(Math.random() * 4)];
      var gm = SCALE[pos] === 5 / 4 || SCALE[pos] === 5 / 3 ? (Math.random() < 0.6 ? 'shake' : 'slide') : Math.random() < 0.25 ? 'slide' : '';
      veena(SCALE[pos], t, i === n - 1 ? 0.2 : 0.16, gm);
      t += i === n - 1 ? 0 : [0.9, 1.2, 1.5, 1.8][Math.floor(Math.random() * 4)];
    }
    timers.push(setTimeout(phrase, (t - ctx.currentTime) * 1000 + 5000 + Math.random() * 6000));
  }

  function start() {
    var c = ac(); if (!c) return;
    playing = true;
    master.gain.cancelScheduledValues(c.currentTime);
    master.gain.setValueAtTime(Math.max(master.gain.value, 0.0001), c.currentTime);
    master.gain.exponentialRampToValueAtTime(0.55, c.currentTime + 4);
    padStart();
    timers.push(setTimeout(function () { if (playing) softBell(SA * 8, 0.06); }, 600));
    timers.push(setTimeout(phrase, 5000));
    timers.push(setTimeout(bells, 30000));
    sync();
  }
  function stop() {
    playing = false;
    timers.forEach(clearTimeout); timers = [];
    if (ctx && master) { var t = ctx.currentTime; master.gain.cancelScheduledValues(t); master.gain.setValueAtTime(Math.max(master.gain.value, 0.0001), t); master.gain.exponentialRampToValueAtTime(0.0001, t + 1.2); padStop(); }
    sync();
  }
  function save(v) { try { localStorage.setItem(KEY, v ? '1' : '0'); } catch (e) {} }
  function wanted() { try { return localStorage.getItem(KEY) === '1'; } catch (e) { return false; } }

  var btn = document.getElementById('sndBtn');
  function sync() {
    if (!btn) return;
    btn.setAttribute('aria-pressed', playing ? 'true' : 'false');
    btn.setAttribute('aria-label', playing ? T.on : T.off);
    btn.title = playing ? T.on : T.off;
    btn.innerHTML = playing ? '<span class="eq"><i></i><i></i><i></i></span>' : '🎵';
  }
  if (btn && !app) {
    btn.hidden = false; sync();
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      btn.classList.remove('ring'); void btn.offsetWidth; btn.classList.add('ring');
      if (playing) { stop(); save(false); } else { start(); save(true); }
    });
    // they left the sound on last time: resume on their first tap anywhere (browsers need a tap before sound)
    if (wanted()) {
      var resume = function () { document.removeEventListener('pointerdown', resume, true); if (!playing && wanted()) start(); };
      document.addEventListener('pointerdown', resume, true);
    }
  }
  document.addEventListener('visibilitychange', function () {
    if (!ctx) return;
    if (document.hidden) ctx.suspend(); else if (playing) ctx.resume();
  });
  window.SJBell = bell;

  // ------------------------------------------------------------- phone menu: the "more" sheet
  var sheet = document.getElementById('msheet'), sheetFrom = null;
  function sheetOpen(o) {
    if (!sheet) return;
    if (o) { sheetFrom = document.activeElement; sheet.hidden = false; requestAnimationFrame(function () { sheet.classList.add('open'); }); document.body.classList.add('noscroll'); var c = sheet.querySelector('.mclose'); if (c) setTimeout(function () { c.focus(); }, 200); }
    else { sheet.classList.remove('open'); document.body.classList.remove('noscroll'); setTimeout(function () { if (!sheet.classList.contains('open')) sheet.hidden = true; }, 260); if (sheetFrom && sheetFrom.focus) sheetFrom.focus(); }
  }
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[data-pick]');
    if (a) { try { localStorage.setItem('sj.langPick', a.getAttribute('data-pick')); localStorage.setItem('jothidam.lang', a.getAttribute('data-pick')); } catch (x) {} }
    if (!sheet) return;
    if (e.target.closest('[data-sheet]')) { sheetOpen(true); return; }
    if (sheet.classList.contains('open') && (e.target === sheet || e.target.closest('[data-sheet-close], .msheet a, .msheet [data-go]'))) sheetOpen(false);
  });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && sheet && sheet.classList.contains('open')) sheetOpen(false); });

  // ------------------------------------------------------------- light a lamp
  var lamp = document.getElementById('lamp');
  if (lamp) {
    var slug = lamp.getAttribute('data-temple'), lkey = 'sj.lamp.' + slug, msg = document.getElementById('lampMsg');
    var lit = function (when) {
      lamp.classList.add('lit');
      if (msg && when) msg.textContent = msg.getAttribute('data-done').replace('{d}', new Date(when).toLocaleDateString(tamil ? 'ta-IN' : 'en-IN', { day: 'numeric', month: 'long', year: 'numeric' }));
    };
    try { var prev = localStorage.getItem(lkey); if (prev && Date.now() - Number(prev) < 86400000) lit(Number(prev)); } catch (e) {}
    lamp.addEventListener('click', function () {
      var now = Date.now();
      lamp.classList.remove('lit'); void lamp.offsetWidth; lit(now);
      if (!app) { ac(); if (master && !playing) { master.gain.setValueAtTime(0.9, ctx.currentTime); } bell(523.25, 0.3); setTimeout(function () { bell(659.25, 0.2); }, 700); if (!playing) setTimeout(function () { if (!playing && master) master.gain.setValueAtTime(0.0001, ctx.currentTime); }, 6000); }
      try { localStorage.setItem(lkey, String(now)); } catch (e) {}
    });
  }

  // ------------------------------------------------------------- open now / closed now (India time)
  document.querySelectorAll('[data-hours]').forEach(function (el) {
    var hrs; try { hrs = JSON.parse(el.getAttribute('data-hours')); } catch (e) { return; }
    var parts = new Intl.DateTimeFormat('en-GB', { timeZone: 'Asia/Kolkata', hour: '2-digit', minute: '2-digit', hour12: false }).formatToParts(new Date());
    var h = 0, m = 0; parts.forEach(function (p) { if (p.type === 'hour') h = Number(p.value) % 24; if (p.type === 'minute') m = Number(p.value); });
    var now = h * 60 + m;
    var fmt = function (mins) { var hh = Math.floor(mins / 60), mm = mins % 60, ap = hh >= 12 ? 'pm' : 'am', h12 = ((hh + 11) % 12) + 1; return h12 + (mm ? ':' + String(mm).padStart(2, '0') : '') + ' ' + ap; };
    var open = null, next = null;
    hrs.forEach(function (r) { var a = r[0] * 60 + r[1], b = r[2] * 60 + r[3]; if (now >= a && now < b) open = b; else if (now < a && next === null) next = a; });
    var L = tamil ? { o: 'இப்போது திறந்திருக்கிறது', c: 'இப்போது மூடியிருக்கிறது', till: '{t} வரை', opens: '{t}-க்குத் திறக்கும்', tom: 'நாளை {t}-க்குத் திறக்கும்' }
                  : { o: 'Open now', c: 'Closed now', till: 'until {t}', opens: 'opens at {t}', tom: 'opens tomorrow at {t}' };
    if (open !== null) { el.className = 'opennow on'; el.innerHTML = '<b>' + L.o + '</b> · ' + L.till.replace('{t}', fmt(open)); }
    else { el.className = 'opennow off'; el.innerHTML = '<b>' + L.c + '</b> · ' + (next !== null ? L.opens.replace('{t}', fmt(next)) : L.tom.replace('{t}', fmt(hrs[0][0] * 60 + hrs[0][1]))); }
    el.hidden = false;
  });
})();
