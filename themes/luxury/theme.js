(function() {
  var doc = window.parent.document;
  var win = window.parent;

  // Cleanup prior elements
  var selectorsToClean = ['#neural-canvas', '#matrix-canvas', '#stars-canvas', '#theme-background-canvas', '#echo-cursor-glow', '.theme-bg-gradient'];
  selectorsToClean.forEach(function(sel) {
    var el = doc.querySelector(sel);
    if (el) { el.remove(); }
  });
  
  var oldStyle = doc.getElementById('theme-dynamic-bg-style');
  if (oldStyle) { oldStyle.remove(); }

  // ── Luxury Gold Particles Canvas Background ───────────────────────────────
  var cvs = doc.createElement('canvas');
  cvs.id = 'theme-background-canvas';
  Object.assign(cvs.style, {
    position:'fixed', top:'0', left:'0', width:'100%', height:'100%',
    pointerEvents:'none', zIndex:'-1', opacity:'0.45'
  });
  doc.body.insertBefore(cvs, doc.body.firstChild);

  var ctx = cvs.getContext('2d');
  var W, H;
  
  function resize(){ W=cvs.width=win.innerWidth; H=cvs.height=win.innerHeight; }
  resize();
  win.addEventListener('resize', resize);

  var particles = [];
  var MAX_PARTICLES = 30;

  function mkParticle() {
    return {
      x: Math.random() * W,
      y: H + Math.random() * 20,
      r: 0.8 + Math.random() * 1.8,
      vx: (Math.random() - 0.5) * 0.15,
      vy: -0.2 - Math.random() * 0.4,
      life: 1.0,
      decay: 0.002 + Math.random() * 0.003
    };
  }

  for (var i = 0; i < MAX_PARTICLES; i++) {
    particles.push(mkParticle());
    particles[i].y = Math.random() * H; // start distributed
  }

  var active = true;

  function drawLuxury() {
    if (!active || !doc.getElementById('theme-background-canvas')) {
      return;
    }
    ctx.clearRect(0, 0, W, H);
    
    // Luxury Matte Black Background
    ctx.fillStyle = '#050505';
    ctx.fillRect(0, 0, W, H);

    // Render golden particles
    particles.forEach(function(p, idx) {
      p.x += p.vx;
      p.y += p.vy;
      p.life -= p.decay;

      if (p.life <= 0 || p.x < 0 || p.x > W || p.y < 0) {
        particles[idx] = mkParticle();
        return;
      }

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(212, 175, 55, ' + (p.life * 0.45) + ')';
      ctx.fill();
    });

    win.requestAnimationFrame(drawLuxury);
  }
  drawLuxury();

  // ── Gold Cursor Glow Ring ──────────────────────────────────────────────────
  var g = doc.createElement('div');
  g.id = 'echo-cursor-glow';
  Object.assign(g.style, {
    position:'fixed', width:'200px', height:'200px', borderRadius:'50%',
    border:'1px solid rgba(212,175,55,0.2)',
    background:'radial-gradient(circle,rgba(212,175,55,0.03) 0%,transparent 65%)',
    pointerEvents:'none', zIndex:'9998', transform:'translate(-50%,-50%)',
    left:'-500px', top:'-500px'
  });
  doc.body.appendChild(g);

  var cx=win.innerWidth/2, cy=win.innerHeight/2, tx=cx, ty=cy;
  function lerp(a,b,t){ return a+(b-a)*t; }
  
  var moveListener = function(e){ tx=e.clientX; ty=e.clientY; };
  doc.addEventListener('mousemove', moveListener);
  
  var runCursor = true;
  (function loop(){
    if (!runCursor || !doc.getElementById('echo-cursor-glow')) {
      doc.removeEventListener('mousemove', moveListener);
      return;
    }
    cx=lerp(cx,tx,0.1); cy=lerp(cy,ty,0.1);
    g.style.left=cx+'px'; g.style.top=cy+'px';
    win.requestAnimationFrame(loop);
  })();

  win.addEventListener('beforeunload', function() {
    active = false;
    runCursor = false;
  });
})();
