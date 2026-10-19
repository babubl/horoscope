/* Suba Jathagam — temple ambience (bell + soft Om drone, synthesised in the browser, no audio files),
   the "light a lamp" diya and the "open now" badge on temple pages.
   Sound never starts by itself: the visitor taps the bell. The choice is remembered on this device,
   and resumes on the next tap anywhere if they left it on. Not shown inside the Android app. */
(function () {
  var app = false;
  try { app = sessionStorage.getItem('jothidam.app') === '1' || /[?&]source=twa\b/.test(location.search); } catch (e) {}
  var KEY = 'sj.sound';
  var ctx = null, master = null, droneNodes = null, bellTimer = null, playing = false;
  var tamil = document.documentElement.lang === 'ta';
  var T = tamil ? { on: 'கோயில் ஒலி நிறுத்த', off: 'கோயில் ஒலி கேட்க' } : { on: 'Stop temple sounds', off: 'Play temple sounds' };

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

  // A soft "Om" drone: low tone with harmonics through a slowly moving vowel filter (aa → oo → mm), breathing in and out.
  function startDrone() {
    var c = ac(); if (!c || droneNodes) return;
    var base = 136.1, now = c.currentTime, nodes = [];
    var g = c.createGain(); g.gain.value = 0.0001; g.connect(master);
    var lp = c.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 700; lp.Q.value = 6; lp.connect(g);
    [[1, 'sawtooth', 0.16], [2, 'sine', 0.12], [1.5, 'sine', 0.05], [0.5, 'sine', 0.22]].forEach(function (h) {
      var o = c.createOscillator(), og = c.createGain();
      o.type = h[1]; o.frequency.value = base * h[0]; o.detune.value = (Math.random() - 0.5) * 4;
      og.gain.value = h[2]; o.connect(og); og.connect(lp); o.start(now); nodes.push(o);
    });
    // vowel sweep (one "Om" about every 9 s) and a breathing swell
    var lfo = c.createOscillator(), lg = c.createGain();
    lfo.frequency.value = 1 / 9; lg.gain.value = 320; lfo.connect(lg); lg.connect(lp.frequency); lfo.start(now); nodes.push(lfo);
    var br = c.createOscillator(), bg = c.createGain();
    br.frequency.value = 1 / 9; bg.gain.value = 0.035; br.connect(bg); bg.connect(g.gain); br.start(now); nodes.push(br);
    g.gain.setValueAtTime(0.0001, now);
    g.gain.exponentialRampToValueAtTime(0.06, now + 3);
    droneNodes = { nodes: nodes, gain: g };
  }
  function stopDrone() {
    if (!droneNodes || !ctx) return;
    var d = droneNodes, t = ctx.currentTime;
    d.gain.gain.cancelScheduledValues(t);
    d.gain.gain.setValueAtTime(Math.max(d.gain.gain.value, 0.0001), t);
    d.gain.gain.exponentialRampToValueAtTime(0.0001, t + 1.5);
    setTimeout(function () { d.nodes.forEach(function (o) { try { o.stop(); } catch (e) {} }); }, 1700);
    droneNodes = null;
  }

  function scheduleBells() {
    clearTimeout(bellTimer);
    bellTimer = setTimeout(function () {
      if (!playing) return;
      var pitches = [392, 440, 523.25, 587.33];
      bell(pitches[Math.floor(Math.random() * pitches.length)], 0.22);
      scheduleBells();
    }, 9000 + Math.random() * 12000);
  }

  function start() {
    var c = ac(); if (!c) return;
    playing = true;
    master.gain.cancelScheduledValues(c.currentTime);
    master.gain.setValueAtTime(Math.max(master.gain.value, 0.0001), c.currentTime);
    master.gain.exponentialRampToValueAtTime(0.9, c.currentTime + 0.4);
    bell(440, 0.34);
    setTimeout(function () { if (playing) bell(523.25, 0.24); }, 1400);
    startDrone(); scheduleBells(); sync();
  }
  function stop() {
    playing = false; clearTimeout(bellTimer); stopDrone(); sync();
  }
  function save(v) { try { localStorage.setItem(KEY, v ? '1' : '0'); } catch (e) {} }
  function wanted() { try { return localStorage.getItem(KEY) === '1'; } catch (e) { return false; } }

  var btn = document.getElementById('sndBtn');
  function sync() {
    if (!btn) return;
    btn.setAttribute('aria-pressed', playing ? 'true' : 'false');
    btn.setAttribute('aria-label', playing ? T.on : T.off);
    btn.title = playing ? T.on : T.off;
    btn.textContent = playing ? '🔔' : '🔕';
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
