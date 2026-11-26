/* The hero background: Graceful Exchange (assets/exchange.js) on a full-width canvas behind the hero.
   The seed fixes the artwork; the drift only runs while the hero is on screen, and rests on one frame
   under reduced motion. */
(function () {
  'use strict';
  const SEED = 7;
  const PARAMS = {
    seed: SEED, lines: 34, speed: 22, stage: 150, swap: 0.42, migrate: 0.035, curve: 0.62,
    weight: 1.25, opacity: 0.55, colors: ['#a8a8a8', '#0f62fe', '#009d9a'], background: '#ffffff'
  };
  const hero = document.querySelector('.hero');
  const canvas = hero && hero.querySelector('canvas.hero-art');
  if (!canvas || !window.GracefulExchange) return;
  const ctx = canvas.getContext('2d');
  const art = new window.GracefulExchange(PARAMS);
  const still = window.matchMedia('(prefers-reduced-motion: reduce)');
  let w = 0, h = 0, offset = 0, last = 0, raf = 0, onScreen = true;

  function size() {
    const r = canvas.getBoundingClientRect(), dpr = Math.min(window.devicePixelRatio || 1, 2);
    w = Math.max(1, Math.round(r.width)); h = Math.max(1, Math.round(r.height));
    canvas.width = Math.round(w * dpr); canvas.height = Math.round(h * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    if (shown()) art.draw(ctx, w, h, offset);
    sync();
  }
  function frame(now) {
    raf = 0;
    if (last) offset += Math.min(0.1, (now - last) / 1000) * PARAMS.speed;   // a long pause never jumps
    last = now;
    art.draw(ctx, w, h, offset);
    if (running()) raf = requestAnimationFrame(frame);
  }
  const shown = () => canvas.offsetParent !== null;   // not drawn where CSS hides it (phones)
  const running = () => onScreen && !document.hidden && !still.matches && shown();
  function sync() {
    if (running() && !raf) { last = 0; raf = requestAnimationFrame(frame); }
    if (!running() && raf) { cancelAnimationFrame(raf); raf = 0; }
  }
  new ResizeObserver(size).observe(canvas);
  new IntersectionObserver((es) => { onScreen = es[es.length - 1].isIntersecting; sync(); }).observe(hero);
  document.addEventListener('visibilitychange', sync);
  still.addEventListener('change', sync);
  size();
  sync();
})();
