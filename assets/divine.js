/* Suba Jathagam — temple ambience (a soft drone with nadaswaram, flute, veena, violin, mandolin or Om chanting
   in real Carnatic ragas, synthesised in the browser, no audio files),
   the "light a lamp" diya and the "open now" badge on temple pages.
   Sound never starts by itself: the visitor taps the bell. The choice is remembered on this device,
   and resumes on the next tap anywhere if they left it on. Not shown inside the Android app. */
(function () {
  var app = false;
  try { app = sessionStorage.getItem('jothidam.app') === '1' || /[?&]source=twa\b/.test(location.search); } catch (e) {}
  var KEY = 'sj.music';
  var ctx = null, master = null, outNode = null, playing = false;
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
      master.connect(comp); comp.connect(ctx.destination); outNode = comp;
    }
    if (ctx.state === 'suspended') ctx.resume();
    return ctx;
  }

  // A temple bell: inharmonic partials with long, different decays, plus a short metallic strike.
  function bell(pitch, vol) {
    var c = ac(); if (!c) return;
    var t0 = c.currentTime + 0.02;
    pitch = pitch || 440; vol = vol || 0.32;
    var out = c.createGain(); out.gain.value = vol; out.connect(outNode || c.destination);
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

  // ---- Divine music: a soft drone under one Carnatic instrument playing slow alapana-style phrases in a real raga,
  // with the gamakas (slides and shakes) that make it sound South Indian. Everything is synthesised here — nothing is
  // downloaded and nothing is copyrighted. The visitor picks the instrument; the choice is remembered.
  var SA = 138.6, reverb = null, timers = [], live = [], ks = {}, track = null;
  var TRACKS = [
    { id: 'nadaswaram', icon: '🎺', ta: 'மங்கல இசை (நாதஸ்வரம்)', te: 'మంగళ వాద్యం (నాదస్వరం)', en: 'Mangala isai (nadaswaram)' },
    { id: 'flute', icon: '🪈', ta: 'புல்லாங்குழல்', te: 'వేణువు', en: 'Flute' },
    { id: 'veena', icon: '🪕', ta: 'வீணை', te: 'వీణ', en: 'Veena' },
    { id: 'violin', icon: '🎻', ta: 'வயலின்', te: 'వయొలిన్', en: 'Violin' },
    { id: 'mandolin', icon: '🎸', ta: 'மாண்டலின்', te: 'మాండొలిన్', en: 'Mandolin' },
    { id: 'om', icon: 'ॐ', ta: 'ஓம் ஜபம்', te: 'ఓం జపం', en: 'Om chanting' }
  ];
  var lng = (document.documentElement.lang || 'en').slice(0, 2);
  // ragas as just-intonation ratios of Sa; G = notes that carry a kampitam (shake)
  var S = 1, R1 = 16 / 15, R2 = 9 / 8, G2 = 6 / 5, G3 = 5 / 4, M1 = 4 / 3, M2 = 45 / 32, P = 3 / 2, D1 = 8 / 5, D2 = 5 / 3, N2 = 9 / 5, N3 = 15 / 8;
  var RAGA = {
    kalyani: { sw: [S, R2, G3, M2, P, D2, N3], shake: [G3, N3, M2], rest: [S, G3, P] },            // mangala isai
    mayamalavagowla: { sw: [S, R1, G3, M1, P, D1, N3], shake: [R1, D1, G3], rest: [S, P, G3] },     // morning raga
    kharaharapriya: { sw: [S, R2, G2, M1, P, D2, N2], shake: [G2, N2, R2], rest: [S, P, R2] },
    shanmukhapriya: { sw: [S, R2, G2, M2, P, D1, N2], shake: [G2, N2, D1], rest: [S, P, M2] },
    keeravani: { sw: [S, R2, G2, M1, P, D1, N3], shake: [G2, D1], rest: [S, P, G2] }
  };
  function hall() {
    if (reverb) return reverb;
    var c = ctx, len = Math.floor(c.sampleRate * 4), buf = c.createBuffer(2, len, c.sampleRate);
    for (var ch = 0; ch < 2; ch++) {
      var d = buf.getChannelData(ch), lp = 0;
      for (var i = 0; i < len; i++) { lp += 0.4 * ((Math.random() * 2 - 1) - lp); d[i] = lp * Math.pow(1 - i / len, 3.2); }
    }
    reverb = c.createConvolver(); reverb.buffer = buf;
    var wet = c.createGain(); wet.gain.value = 0.55; reverb.connect(wet); wet.connect(master);
    return reverb;
  }
  function voice(dry, wet) { var g = ctx.createGain(), w = ctx.createGain(), d = ctx.createGain(); w.gain.value = wet == null ? 1 : wet; d.gain.value = dry; g.connect(w); w.connect(hall()); g.connect(d); d.connect(master); return g; }
  function later(fn, ms) { timers.push(setTimeout(function () { if (playing) fn(); }, ms)); }
  function pick(a) { return a[Math.floor(Math.random() * a.length)]; }

  // ---- plucked strings (Karplus–Strong). bright: a pick (mandolin) or a finger (veena); jawari: the tanpura's buzz
  function pluckBuf(f, opt) {
    var key = f + '|' + (opt.bright ? 1 : 0) + (opt.jawari ? 1 : 0); if (ks[key]) return ks[key];
    var sr = ctx.sampleRate, N = Math.max(2, Math.round(sr / f)), len = Math.floor(sr * (opt.len || 4)), buf = ctx.createBuffer(1, len, sr), d = buf.getChannelData(0);
    var ring = new Float32Array(N), i, k = 0, mx = 0, loss = opt.loss || 0.4992;
    for (i = 0; i < N; i++) ring[i] = Math.random() * 2 - 1;
    for (var pass = 0; pass < (opt.bright ? 0 : 3); pass++) for (i = 1; i < N; i++) ring[i] = 0.5 * (ring[i] + ring[i - 1]);
    for (i = 0; i < len; i++) {
      var a = ring[k], b = ring[(k + 1) % N];
      d[i] = opt.jawari ? Math.tanh(a * 2.2) + 0.25 * a : a;
      ring[k] = loss * (a + b); k = (k + 1) % N;
      if (Math.abs(d[i]) > mx) mx = Math.abs(d[i]);
    }
    var fade = Math.floor(sr * 0.5);
    for (i = 0; i < len; i++) { d[i] /= mx || 1; if (i > len - fade) d[i] *= (len - i) / fade; }
    return (ks[key] = buf);
  }
  // rate automation for a gamaka on a playback-rate or frequency AudioParam
  function gamaka(p, base, ratio, t, dur, kind, from) {
    var f = base * ratio;
    if (kind === 'slide') { p.setValueAtTime(base * (from || ratio * 0.94), t); p.linearRampToValueAtTime(f, t + Math.min(0.25, dur * 0.4)); }
    else if (kind === 'shake') {
      p.setValueAtTime(f, t); var q = t + Math.min(0.2, dur * 0.25), w = 0.17;
      while (q + w * 2 < t + dur - 0.1) { p.linearRampToValueAtTime(f * 1.045, q + w); p.linearRampToValueAtTime(f, q + w * 2); q += w * 2; }
    } else p.setValueAtTime(f, t);
  }

  // ---- the drone: soft pure tones on Sa, Pa and upper Sa that swell and fade slowly, like breath (no strings)
  function hum(vol) {
    var t = ctx.currentTime, lp = ctx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 900; lp.connect(voice(0.6, 0.8));
    [[SA, 0.05, 0.07], [SA * 1.5, 0.025, 0.05], [SA * 2, 0.03, 0.09], [SA * 2.003, 0.02, 0.11]].forEach(function (v) {
      var o = ctx.createOscillator(), g = ctx.createGain(), lfo = ctx.createOscillator(), lg = ctx.createGain();
      o.type = 'sine'; o.frequency.value = v[0];
      g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(v[1] * vol * 2, t + 5);
      lfo.frequency.value = v[2]; lg.gain.value = v[1] * vol * 0.9; lfo.connect(lg); lg.connect(g.gain);
      o.connect(g); g.connect(lp); o.start(t); lfo.start(t); live.push(o, lfo);
    });
  }
  // ---- sustained instruments (nadaswaram, flute, violin): one oscillator voice that glides from note to note
  function sustained(kind) {
    var base = kind === 'flute' ? SA * 4 : SA * 2, t0 = ctx.currentTime;
    var o1 = ctx.createOscillator(), o2 = ctx.createOscillator(), amp = ctx.createGain(), lfo = ctx.createOscillator(), lg = ctx.createGain(), out = ctx.createGain();
    o1.type = kind === 'flute' ? 'sine' : 'sawtooth';
    o2.type = kind === 'nadaswaram' ? 'square' : kind === 'flute' ? 'triangle' : 'sawtooth';
    o2.detune.value = kind === 'flute' ? 1200 : 6;
    var g2 = ctx.createGain(); g2.gain.value = kind === 'flute' ? 0.08 : kind === 'nadaswaram' ? 0.45 : 0.6;
    amp.gain.value = 0.0001;
    lfo.frequency.value = kind === 'violin' ? 5.8 : 5.2; lg.gain.value = 0;
    lfo.connect(lg); lg.connect(o1.frequency); lg.connect(o2.frequency);
    var chain;
    if (kind === 'nadaswaram') {
      var hp = ctx.createBiquadFilter(); hp.type = 'highpass'; hp.frequency.value = 280;
      var f1 = ctx.createBiquadFilter(); f1.type = 'peaking'; f1.frequency.value = 1150; f1.Q.value = 1.6; f1.gain.value = 9;
      var f2 = ctx.createBiquadFilter(); f2.type = 'peaking'; f2.frequency.value = 2700; f2.Q.value = 2; f2.gain.value = 5;
      var lp = ctx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 4800;
      hp.connect(f1); f1.connect(f2); f2.connect(lp); chain = [hp, lp]; out.gain.value = 0.11;
    } else if (kind === 'violin') {
      var lpv = ctx.createBiquadFilter(); lpv.type = 'lowpass'; lpv.frequency.value = 3400;
      var b1 = ctx.createBiquadFilter(); b1.type = 'peaking'; b1.frequency.value = 290; b1.Q.value = 1.4; b1.gain.value = 5;
      var b2 = ctx.createBiquadFilter(); b2.type = 'peaking'; b2.frequency.value = 2900; b2.Q.value = 1.2; b2.gain.value = 4;
      lpv.connect(b1); b1.connect(b2); chain = [lpv, b2]; out.gain.value = 0.12;
    } else {
      var lpf = ctx.createBiquadFilter(); lpf.type = 'lowpass'; lpf.frequency.value = 2600; chain = [lpf, lpf]; out.gain.value = 0.2;
      // breath: soft filtered noise that follows the note's loudness
      var nb = ctx.createBuffer(1, ctx.sampleRate * 2, ctx.sampleRate), nd = nb.getChannelData(0);
      for (var i = 0; i < nd.length; i++) nd[i] = Math.random() * 2 - 1;
      var ns = ctx.createBufferSource(); ns.buffer = nb; ns.loop = true;
      var bp = ctx.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.value = 1900; bp.Q.value = 0.9;
      var ng = ctx.createGain(); ng.gain.value = 0.05; ns.connect(bp); bp.connect(ng); ng.connect(amp); ns.start(t0); live.push(ns);
    }
    o1.connect(amp); o2.connect(g2); g2.connect(amp); amp.connect(chain[0]); chain[1].connect(out); out.connect(voice(0.6, 0.9));
    o1.start(t0); o2.start(t0); lfo.start(t0); live.push(o1, o2, lfo);
    var att = kind === 'violin' ? 0.14 : kind === 'flute' ? 0.09 : 0.05;
    return {
      note: function (ratio, t, dur, gm, from) {
        gamaka(o1.frequency, base, ratio, t, dur, gm, from && base * from); gamaka(o2.frequency, base, ratio, t, dur, gm, from && base * from);
        var a = amp.gain; a.setTargetAtTime(kind === 'flute' ? 0.9 : 0.75, t, att);
        // vibrato blooms on long notes (not on shaken ones)
        lg.gain.setValueAtTime(0, t); if (dur > 1 && gm !== 'shake') lg.gain.linearRampToValueAtTime(base * ratio * (kind === 'violin' ? 0.007 : 0.004), t + dur * 0.8);
      },
      rest: function (t) { amp.gain.setTargetAtTime(0.0001, t, 0.18); lg.gain.setValueAtTime(0, t); }
    };
  }
  // ---- plucked melody instruments
  function plucker(kind) {
    var base = kind === 'mandolin' ? SA * 4 : SA * 2, bus = ctx.createGain();
    var lp = ctx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = kind === 'mandolin' ? 5200 : 2400;
    var pk = ctx.createBiquadFilter(); pk.type = 'peaking'; pk.frequency.value = kind === 'mandolin' ? 1800 : 280; pk.gain.value = 4; pk.Q.value = 0.8;
    bus.gain.value = kind === 'mandolin' ? 0.3 : 0.36; bus.connect(lp); lp.connect(pk); pk.connect(voice(0.55, 0.85));
    function one(ratio, t, dur, gm, from, vol, det) {
      var src = ctx.createBufferSource(), g = ctx.createGain();
      src.buffer = pluckBuf(base, { bright: kind === 'mandolin', len: 4 });
      gamaka(src.playbackRate, 1, ratio * (det || 1), t, dur, gm, from);
      g.gain.value = vol; src.connect(g); g.connect(bus); src.start(t); src.stop(t + Math.min(4, dur + 2.5));
    }
    return {
      note: function (ratio, t, dur, gm, from) {
        if (kind === 'mandolin') {
          one(ratio, t, dur, gm, from, 0.8, 1); one(ratio, t + 0.004, dur, gm, from, 0.6, 1.003);      // two strings per course
          if (dur > 1.2) for (var q = t + 0.11; q < t + dur - 0.15; q += 0.105) one(ratio, q, 0.3, '', 0, 0.32, 1); // tremolo on long notes
        } else one(ratio, t, dur, gm, from, 0.85, 1);
      },
      rest: function () {}
    };
  }
  // ---- alapana: slow phrases that climb or fall through the raga and rest on its resting notes
  function alapana(inst, raga, pace) {
    var R = RAGA[raga], sc = [], i;
    for (i = 4; i < 7; i++) sc.push(R.sw[i] / 2);                 // lower Pa Da Ni
    for (i = 0; i < 7; i++) sc.push(R.sw[i]);
    sc.push(2); sc.push(R.sw[1] * 2); sc.push(R.sw[2] * 2);          // upper Sa Ri Ga
    var pos = 3, last = null;
    function isRest(r) { return R.rest.some(function (x) { return Math.abs(x - r) < 1e-6 || Math.abs(x * 2 - r) < 1e-6 || Math.abs(x / 2 - r) < 1e-6; }); }
    function isShake(r) { return R.shake.some(function (x) { return Math.abs(x - r) < 1e-6 || Math.abs(x * 2 - r) < 1e-6 || Math.abs(x / 2 - r) < 1e-6; }); }
    (function phrase() {
      var t = ctx.currentTime + 0.1, n = 4 + Math.floor(Math.random() * 5), dir = pos < 5 ? 1 : pos > 9 ? -1 : pick([1, -1]);
      for (var k = 0; k < n; k++) {
        var step = Math.random() < 0.75 ? dir : (Math.random() < 0.5 ? -dir : 2 * dir);
        pos = Math.max(0, Math.min(sc.length - 1, pos + step));
        if (k === n - 1) { while (!isRest(sc[pos]) && pos > 0) pos--; }
        var r = sc[pos], dur = (k === n - 1 ? pick([2.2, 2.8, 3.4]) : pick([0.45, 0.6, 0.6, 0.9, 1.2])) * pace;
        var gm = isShake(r) && dur > 0.55 ? 'shake' : last && Math.random() < 0.35 ? 'slide' : '';
        inst.note(r, t, dur, gm, last);
        last = r; t += dur;
      }
      inst.rest(t);
      later(phrase, (t - ctx.currentTime) * 1000 + 2200 + Math.random() * 3500);
    })();
  }
  // ---- thavil: the soft beat under mangala isai (adi talam, eight beats)
  function thavil() {
    var beat = 60 / 76, pat = [1, 0, 2, 2, 1, 0, 2, 0], i = 0, bus = voice(0.6, 0.3); var bg = ctx.createGain(); bg.gain.value = 0.22; bg.connect(bus);
    (function hit() {
      var t = ctx.currentTime + 0.05, k = pat[i % 8];
      if (k === 1) { var o = ctx.createOscillator(), g = ctx.createGain(); o.frequency.setValueAtTime(110, t); o.frequency.exponentialRampToValueAtTime(58, t + 0.25); g.gain.setValueAtTime(0.9, t); g.gain.exponentialRampToValueAtTime(0.0001, t + 0.35); o.connect(g); g.connect(bg); o.start(t); o.stop(t + 0.4); }
      if (k === 2) { var n = ctx.createBufferSource(), b = ctx.createBuffer(1, Math.floor(ctx.sampleRate * 0.08), ctx.sampleRate), dd = b.getChannelData(0); for (var j = 0; j < dd.length; j++) dd[j] = (Math.random() * 2 - 1) * Math.pow(1 - j / dd.length, 4); n.buffer = b; var f = ctx.createBiquadFilter(); f.type = 'bandpass'; f.frequency.value = 1500; f.Q.value = 1.5; var ng = ctx.createGain(); ng.gain.value = 0.7; n.connect(f); f.connect(ng); ng.connect(bg); n.start(t); }
      i++; later(hit, beat * 1000);
    })();
  }
  // ---- Om: a chorus of low voices, "O–o–mmm", breath and again
  function om() {
    var shapes = { a: [700, 1150, 2700], o: [450, 800, 2830], u: [330, 700, 2500] };
    (function chant() {
      var t = ctx.currentTime + 0.1, L = 7.5;
      [[SA, 0, 0.55, -0.4], [SA * 1.0025, 0.04, 0.45, 0.4], [SA / 2, 0.08, 0.5, 0]].forEach(function (v) {
        var o = ctx.createOscillator(), g = ctx.createGain(), pan = ctx.createStereoPanner ? ctx.createStereoPanner() : null;
        o.type = 'sawtooth'; o.frequency.setValueAtTime(v[0] * 0.97, t + v[1]); o.frequency.linearRampToValueAtTime(v[0], t + v[1] + 0.4);
        var sum = ctx.createGain(); sum.gain.value = 1;
        var fs = [0, 1, 2].map(function (k) {
          var f = ctx.createBiquadFilter(); f.type = 'bandpass'; f.Q.value = [6, 8, 10][k];
          var fg = ctx.createGain(); fg.gain.value = [1, 0.5, 0.18][k];
          f.frequency.setValueAtTime(shapes.a[k], t); f.frequency.linearRampToValueAtTime(shapes.o[k], t + 0.9); f.frequency.setValueAtTime(shapes.o[k], t + 3.2); f.frequency.linearRampToValueAtTime(shapes.u[k], t + 4.2);
          o.connect(f); f.connect(fg); fg.connect(sum); return fg;
        });
        // "mmm": the mouth closes — the formants fade and a low hum remains
        var hum = ctx.createBiquadFilter(); hum.type = 'lowpass'; hum.frequency.value = 320; var hg = ctx.createGain(); hg.gain.setValueAtTime(0, t); hg.gain.setValueAtTime(0, t + 4); hg.gain.linearRampToValueAtTime(1.4, t + 4.6);
        o.connect(hum); hum.connect(hg); hg.connect(g);
        fs.forEach(function (fg, k) { fg.gain.setValueAtTime(fg.gain.value, t + 4); fg.gain.linearRampToValueAtTime(0.0001, t + 4.8); });
        sum.connect(g);
        g.gain.setValueAtTime(0.0001, t + v[1]); g.gain.linearRampToValueAtTime(v[2] * 0.25, t + v[1] + 0.35); g.gain.setValueAtTime(v[2] * 0.25, t + L - 1.6); g.gain.linearRampToValueAtTime(0.0001, t + L);
        if (pan) { pan.pan.value = v[3]; g.connect(pan); pan.connect(voice(0.55, 1)); } else g.connect(voice(0.55, 1));
        o.start(t + v[1]); o.stop(t + L + 0.1);
      });
      later(chant, (L + 1.6) * 1000);
    })();
  }
  var PLAN = {
    nadaswaram: function () { hum(0.35); var v = sustained('nadaswaram'); later(function () { alapana(v, 'kalyani', 1); }, 1500); later(thavil, 9000); },
    flute: function () { hum(0.45); var v = sustained('flute'); later(function () { alapana(v, 'mayamalavagowla', 1.15); }, 2500); },
    veena: function () { hum(0.4); var v = plucker('veena'); later(function () { alapana(v, 'kharaharapriya', 1.1); }, 2500); },
    violin: function () { hum(0.4); var v = sustained('violin'); later(function () { alapana(v, 'shanmukhapriya', 1.2); }, 2500); },
    mandolin: function () { hum(0.4); var v = plucker('mandolin'); later(function () { alapana(v, 'keeravani', 0.9); }, 2000); },
    om: function () { hum(0.5); later(om, 1200); }
  };
  // a small, far-off temple bell: only the pure partials, deep in the reverb
  function softBell(pitch, vol) {
    var t0 = ctx.currentTime + 0.05, out = voice(0.25); var og = ctx.createGain(); og.gain.value = vol; og.connect(out);
    [[1, 1, 5], [2.01, 0.35, 3.5], [2.76, 0.18, 2.4], [5.4, 0.06, 1.2]].forEach(function (p) {
      var o = ctx.createOscillator(), g = ctx.createGain(); o.type = 'sine'; o.frequency.value = pitch * p[0];
      g.gain.setValueAtTime(0.0001, t0); g.gain.exponentialRampToValueAtTime(p[1], t0 + 0.03); g.gain.exponentialRampToValueAtTime(0.0001, t0 + p[2]);
      o.connect(g); g.connect(og); o.start(t0); o.stop(t0 + p[2] + 0.1);
    });
  }

  var TKEY = 'sj.track';
  function current() { var v; try { v = localStorage.getItem(TKEY); } catch (e) {} return PLAN[v] ? v : 'flute'; }
  function start(id) {
    var c = ac(); if (!c) return;
    if (playing) stop(true);
    track = PLAN[id] ? id : current();
    try { localStorage.setItem(TKEY, track); } catch (e) {}
    playing = true;
    // a fresh output for every start, so the tail of the last instrument fades on its own
    master = c.createGain(); master.gain.setValueAtTime(0.0001, c.currentTime); master.connect(outNode || c.destination);
    reverb = null;
    master.gain.exponentialRampToValueAtTime(1, c.currentTime + 3);
    PLAN[track]();
    sync();
    if (window.SJLook) window.SJLook.render();
  }
  function stop(quiet) {
    playing = false;
    timers.forEach(clearTimeout); timers = [];
    if (ctx && master) {
      var t = ctx.currentTime, m = master, l = live; live = [];
      m.gain.cancelScheduledValues(t); m.gain.setValueAtTime(Math.max(m.gain.value, 0.0001), t); m.gain.exponentialRampToValueAtTime(0.0001, t + 1.2);
      setTimeout(function () { l.forEach(function (o) { try { o.stop(); } catch (e) {} }); try { m.disconnect(); } catch (e) {} }, 1500);
    }
    if (!quiet) { sync(); if (window.SJLook) window.SJLook.render(); }
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
  if (!app) {
    window.SJMusic = {
      tracks: function () { return TRACKS.map(function (x) { return { id: x.id, icon: x.icon, name: x[lng] || x.en }; }); },
      current: current, playing: function () { return playing; },
      play: function (id) { start(id); save(true); }, stop: function () { stop(); save(false); }
    };
  }
  if (btn && !app) {
    btn.hidden = false; sync();
    // the 🎵 button starts the last chosen music and opens the list of instruments; tap again to choose or stop
    btn.setAttribute('data-look-open', 'music');
    btn.addEventListener('click', function () {
      btn.classList.remove('ring'); void btn.offsetWidth; btn.classList.add('ring');
      if (!playing) { start(); save(true); }
    });
    // they left the sound on last time: resume on their first tap anywhere (browsers need a tap before sound)
    if (wanted()) {
      var resume = function (e) { document.removeEventListener('pointerdown', resume, true); if (!playing && wanted() && !(e.target.closest && e.target.closest('#sndBtn, [data-track]'))) start(); };
      document.addEventListener('pointerdown', resume, true);
    }
  }
  if (window.SJLook) window.SJLook.render();
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
      if (!app) { ac(); bell(523.25, 0.3); setTimeout(function () { bell(659.25, 0.2); }, 700); }
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
