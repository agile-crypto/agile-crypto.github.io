/* Graceful Exchange: a seeded, endless braid of strands that trade places and change colour without
   breaking (see art/graceful-exchange.md). Plain Canvas 2D, no dependencies. The same seed always gives
   the same artwork: every swap and every colour change is a hash of (seed, stage, lane or strand), and
   the drift is an accumulated distance, so a frame depends only on the seed and how far the field moved.

   Use:  const art = new GracefulExchange({ seed: 7, lines: 34, ... });
         art.draw(ctx, widthCss, heightCss, offsetPx);   // ctx already scaled for devicePixelRatio */
(function (root) {
  'use strict';

  // a 32-bit integer hash to [0, 1): deterministic on every engine
  function hash(seed, a, b) {
    let x = (seed | 0) ^ Math.imul((a | 0) + 0x7f4a7c15, 0x9e3779b1) ^ Math.imul((b | 0) + 0x632be5ab, 0x85ebca77);
    x ^= x >>> 16; x = Math.imul(x, 0x7feb352d);
    x ^= x >>> 15; x = Math.imul(x, 0x846ca68b);
    x ^= x >>> 16;
    return (x >>> 0) / 4294967296;
  }
  function rgb(hex) {
    const h = String(hex).replace('#', '');
    const n = parseInt(h.length === 3 ? h.replace(/./g, '$&$&') : h, 16);
    return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
  }
  const css = (c) => `rgb(${c[0]},${c[1]},${c[2]})`;

  const DEFAULTS = {
    seed: 7,
    lines: 34,          // strands (line count)
    speed: 22,          // drift in px per second
    stage: 150,         // px between exchange stages
    swap: 0.42,         // chance that an adjacent pair trades at a stage
    migrate: 0.035,     // chance that a strand changes colour at a stage
    curve: 0.62,        // share of a stage the crossing takes
    weight: 1.25,       // line width in px
    opacity: 0.55,
    colors: ['#a8a8a8', '#0f62fe', '#009d9a'],   // before, after, second generation
    background: '#ffffff'
  };

  function GracefulExchange(params) { this.set(params || {}); }

  GracefulExchange.prototype.set = function (params) {
    this.p = Object.assign({}, DEFAULTS, this.p || {}, params);
    this.p.lines = Math.max(2, Math.round(this.p.lines));
    this.rgbs = this.p.colors.map(rgb);
    this.bg = rgb(this.p.background);
    this.cache = new Map();
    this.cache.set(0, this.initial());
  };

  // stage 0: strands in order, all in the first generation
  GracefulExchange.prototype.initial = function () {
    const n = this.p.lines, perm = new Int16Array(n), ver = new Uint8Array(n);
    for (let i = 0; i < n; i++) perm[i] = i;   // perm[lane] = strand
    return { perm, ver };
  };

  // the configuration after the exchanges at stage k (k >= 0), computed forward from the nearest cached stage
  GracefulExchange.prototype.state = function (k) {
    if (k <= 0) return this.cache.get(0);
    if (this.cache.has(k)) return this.cache.get(k);
    let j = k - 1;
    while (j > 0 && !this.cache.has(j)) j--;
    let s = this.cache.get(j);
    const n = this.p.lines, seed = this.p.seed;
    for (let q = j + 1; q <= k; q++) {
      const perm = Int16Array.from(s.perm), ver = Uint8Array.from(s.ver);
      for (let i = q & 1; i + 1 < n; i += 2) {             // odd-even rhythm: disjoint pairs only
        if (hash(seed, q, i) < this.p.swap) { const t = perm[i]; perm[i] = perm[i + 1]; perm[i + 1] = t; }
      }
      for (let st = 0; st < n; st++) {
        if (hash(seed ^ 0x5bd1e995, q, st + 4096) < this.p.migrate && ver[st] < 2) ver[st]++;
      }
      s = { perm, ver };
      this.cache.set(q, s);
    }
    // keep the cache small: the field only moves forward
    if (this.cache.size > 96) for (const key of this.cache.keys()) { if (key !== 0 && key < k - 48) this.cache.delete(key); }
    return s;
  };

  GracefulExchange.prototype.draw = function (ctx, w, h, offset) {
    const p = this.p, n = p.lines, S = p.stage;
    ctx.save();
    ctx.fillStyle = css(this.bg);
    ctx.fillRect(0, 0, w, h);
    const pad = h * 0.04, lane = (h - 2 * pad) / n;
    const Y = (l) => pad + (l + 0.5) * lane;
    const k0 = Math.max(0, Math.floor(offset / S) - 1), k1 = Math.floor((offset + w) / S) + 2;
    // lane of each strand at every visible stage, and its generation
    const lanes = [], vers = [];
    for (let k = k0; k <= k1; k++) {
      const s = this.state(k), inv = new Int16Array(n);
      for (let l = 0; l < n; l++) inv[s.perm[l]] = l;
      lanes.push(inv); vers.push(s.ver);
    }
    const X = (k) => k * S - offset;
    const cw = S * p.curve;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    const halo = css(this.bg);
    const visible = (x) => x <= w + S && x + S >= -S;
    // one strand at a time: first its halo where it crosses, then its line, so a strand only ever cuts the
    // strands drawn before it (the weave) and never its own line
    for (let st = 0; st < n; st++) {
      const wgt = p.weight * (0.7 + 0.8 * hash(p.seed ^ 0x27d4eb2d, st, 77));   // depth: some strands nearer
      const pt = [];                                       // the strand's knots: x, lane y before and after
      for (let idx = 1; idx < lanes.length; idx++) {
        const k = k0 + idx, x = X(k);
        if (!visible(x)) continue;
        pt.push({ x, ya: Y(lanes[idx - 1][st]), yb: Y(lanes[idx][st]), va: vers[idx - 1][st], vb: vers[idx][st] });
      }
      if (!pt.length) continue;
      const piece = (q, from) => {                         // the path of one stage: crossing, then a straight run
        if (from) ctx.moveTo(q.x, q.ya);
        if (q.ya !== q.yb) ctx.bezierCurveTo(q.x + cw * 0.5, q.ya, q.x + cw * 0.5, q.yb, q.x + cw, q.yb);
        else ctx.lineTo(q.x + cw, q.yb);
        ctx.lineTo(q.x + S, q.yb);
      };
      // halo: only the crossings
      ctx.globalAlpha = 1; ctx.strokeStyle = halo; ctx.lineWidth = wgt + 5;
      for (const q of pt) {
        if (q.ya === q.yb) continue;
        ctx.beginPath(); ctx.moveTo(q.x + 2, q.ya);
        ctx.bezierCurveTo(q.x + cw * 0.5, q.ya, q.x + cw * 0.5, q.yb, q.x + cw - 2, q.yb);
        ctx.stroke();
      }
      // line: one path per colour run, a gradient piece where the colour hands over
      ctx.globalAlpha = p.opacity; ctx.lineWidth = wgt;
      const col = (v) => css(this.rgbs[Math.min(v, this.rgbs.length - 1)]);
      let open = false;
      for (let i = 0; i < pt.length; i++) {
        const q = pt[i];
        if (q.va !== q.vb) {
          if (open) { ctx.stroke(); open = false; }
          const g = ctx.createLinearGradient(q.x, 0, q.x + cw, 0);
          g.addColorStop(0, col(q.va)); g.addColorStop(1, col(q.vb));
          ctx.beginPath(); piece(q, true); ctx.strokeStyle = g; ctx.stroke();
          const m = Math.max(3, wgt * 3);                  // a square marks the version change
          ctx.fillStyle = col(q.vb); ctx.fillRect(q.x + cw - m / 2, q.yb - m / 2, m, m);
          continue;
        }
        if (!open) { ctx.beginPath(); ctx.strokeStyle = col(q.vb); piece(q, true); open = true; }
        else piece(q, false);
      }
      if (open) ctx.stroke();
    }
    ctx.restore();
  };

  GracefulExchange.DEFAULTS = DEFAULTS;
  GracefulExchange.hash = hash;
  root.GracefulExchange = GracefulExchange;
})(typeof window !== 'undefined' ? window : globalThis);
