/* Suba Jathagam — temple ambience (bell + soft Om drone, synthesised in the browser, no audio files),
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

  // ---- Divine music: a tanpura drone (Pa–Sa–Sa–Sa) with a slow, flute-like melody in raga Mohanam,
  // all synthesised here, with a soft hall reverb. Nothing is downloaded and nothing is copyrighted.
  var SA = 138.6, reverb = null, timers = [];
  function hall() {
    if (reverb) return reverb;
    var c = ctx, len = Math.floor(c.sampleRate * 3.2), buf = c.createBuffer(2, len, c.sampleRate);
    for (var ch = 0; ch < 2; ch++) { var d = buf.getChannelData(ch); for (var i = 0; i < len; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, 2.6); }
    reverb = c.createConvolver(); reverb.buffer = buf;
    var wet = c.createGain(); wet.gain.value = 0.55; reverb.connect(wet); wet.connect(master);
    return reverb;
  }
  function voice(dest, dry) { var g = ctx.createGain(); g.connect(hall()); if (dry) { var d = ctx.createGain(); d.gain.value = dry; g.connect(d); d.connect(master); } return g; }
  // one tanpura pluck: bright attack that mellows, long ringing decay
  function pluck(f, t, vol) {
    var o = ctx.createOscillator(), o2 = ctx.createOscillator(), lp = ctx.createBiquadFilter(), bp = ctx.createBiquadFilter(), g = ctx.createGain(), out = voice(null, 0.5);
    o.type = 'sawtooth'; o.frequency.value = f; o2.type = 'sawtooth'; o2.frequency.value = f * 1.002;
    lp.type = 'lowpass'; lp.frequency.setValueAtTime(3200, t); lp.frequency.exponentialRampToValueAtTime(700, t + 2.5);
    bp.type = 'peaking'; bp.frequency.setValueAtTime(f * 9, t); bp.frequency.exponentialRampToValueAtTime(f * 4, t + 3); bp.Q.value = 3; bp.gain.value = 7; // the "jivari" shimmer
    g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(vol, t + 0.02); g.gain.exponentialRampToValueAtTime(0.0001, t + 4.6);
    o.connect(lp); o2.connect(lp); lp.connect(bp); bp.connect(g); g.connect(out);
    o.start(t); o2.start(t); o.stop(t + 4.8); o2.stop(t + 4.8);
  }
  function tanpuraLoop() {
    if (!playing) return;
    var t = ctx.currentTime + 0.05, gap = 1.05;
    [[SA * 0.75, 0.05], [SA, 0.045], [SA, 0.045], [SA / 2, 0.06]].forEach(function (s, i) { pluck(s[0], t + i * gap, s[1]); });
    timers.push(setTimeout(tanpuraLoop, gap * 4 * 1000 + 300));
  }
  // a flute-like note: soft attack, gentle vibrato that grows, breath noise
  function flute(f, t, dur, vol) {
    var o = ctx.createOscillator(), o2 = ctx.createOscillator(), g = ctx.createGain(), out = voice(null, 0.35);
    o.type = 'sine'; o.frequency.value = f; o2.type = 'triangle'; o2.frequency.value = f * 2; var g2 = ctx.createGain(); g2.gain.value = 0.08;
    var vib = ctx.createOscillator(), vg = ctx.createGain(); vib.frequency.value = 5.2; vg.gain.setValueAtTime(0, t); vg.gain.linearRampToValueAtTime(f * 0.006, t + Math.min(dur, 1.2));
    vib.connect(vg); vg.connect(o.frequency); vg.connect(o2.frequency);
    g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(vol, t + 0.18); g.gain.setValueAtTime(vol, t + dur - 0.25); g.gain.exponentialRampToValueAtTime(0.0001, t + dur + 0.35);
    o.connect(g); o2.connect(g2); g2.connect(g); g.connect(out);
    var n = ctx.createBufferSource(), nb = ctx.createBuffer(1, Math.floor(ctx.sampleRate * (dur + 0.4)), ctx.sampleRate), nd = nb.getChannelData(0);
    for (var i = 0; i < nd.length; i++) nd[i] = Math.random() * 2 - 1;
    n.buffer = nb; var nf = ctx.createBiquadFilter(); nf.type = 'bandpass'; nf.frequency.value = f * 2; nf.Q.value = 1.5; var ng = ctx.createGain(); ng.gain.value = vol * 0.12;
    n.connect(nf); nf.connect(ng); ng.connect(g);
    [o, o2, vib, n].forEach(function (x) { x.start(t); x.stop(t + dur + 0.5); });
  }
  // Mohanam: Sa Ri2 Ga3 Pa Da2 — gentle phrases that wander a step at a time and rest on Sa, Ga or Pa
  var SCALE = [1, 9 / 8, 5 / 4, 3 / 2, 5 / 3, 2, 9 / 4, 5 / 2];
  var pos = 3;
  function phrase() {
    if (!playing) return;
    var t = ctx.currentTime + 0.1, n = 4 + Math.floor(Math.random() * 5);
    for (var i = 0; i < n; i++) {
      var step = [-2, -1, -1, 1, 1, 2, 0][Math.floor(Math.random() * 7)];
      pos = Math.max(0, Math.min(SCALE.length - 1, pos + step));
      if (i === n - 1) pos = [0, 2, 3, 5][Math.floor(Math.random() * 4)];
      var dur = i === n - 1 ? 2.6 + Math.random() * 1.6 : [0.6, 0.9, 1.2, 1.6][Math.floor(Math.random() * 4)];
      flute(SA * 2 * SCALE[pos], t, dur, 0.055);
      t += dur + 0.05;
    }
    timers.push(setTimeout(phrase, (t - ctx.currentTime) * 1000 + 3000 + Math.random() * 5000));
  }

  function start() {
    var c = ac(); if (!c) return;
    playing = true;
    master.gain.cancelScheduledValues(c.currentTime);
    master.gain.setValueAtTime(Math.max(master.gain.value, 0.0001), c.currentTime);
    master.gain.exponentialRampToValueAtTime(0.8, c.currentTime + 2.5);
    tanpuraLoop();
    timers.push(setTimeout(phrase, 4500));
    sync();
  }
  function stop() {
    playing = false;
    timers.forEach(clearTimeout); timers = [];
    if (ctx && master) { var t = ctx.currentTime; master.gain.cancelScheduledValues(t); master.gain.setValueAtTime(Math.max(master.gain.value, 0.0001), t); master.gain.exponentialRampToValueAtTime(0.0001, t + 1.2); }
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
