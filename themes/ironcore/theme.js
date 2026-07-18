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

  // ── Embers / Industrial Canvas Background ─────────────────────────────────
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
  var MAX_PARTICLES = 60;

  function mkParticle() {
    return {
      x: Math.random() * W,
      y: H + Math.random() * 20,
      r: 1 + Math.random() * 2.5,
      vx: (Math.random() - 0.5) * 0.5,
      vy: -0.8 - Math.random() * 1.2,
      life: 1.0,
      decay: 0.005 + Math.random() * 0.008,
      hue: Math.random() < 0.7 ? 35 : 0 // Gold (35) or Red (0)
    };
  }

  for (var i = 0; i < MAX_PARTICLES; i++) {
    particles.push(mkParticle());
    particles[i].y = Math.random() * H; // start distributed
  }

  var active = true;

  function drawEmbers() {
    if (!active || !doc.getElementById('theme-background-canvas')) {
      return;
    }
    ctx.clearRect(0, 0, W, H);
    
    // Ambient hex background representation or simple wire mesh
    ctx.strokeStyle = 'rgba(239, 68, 68, 0.02)';
    ctx.lineWidth = 1;
    var size = 40;
    for (var x = 0; x < W; x += size * 1.5) {
      for (var y = 0; y < H; y += size * Math.sqrt(3)) {
        ctx.beginPath();
        for (var angle = 0; angle < 6; angle++) {
          var x_i = x + size * Math.cos(angle * Math.PI / 3);
          var y_i = y + size * Math.sin(angle * Math.PI / 3);
          if (angle === 0) ctx.moveTo(x_i, y_i);
          else ctx.lineTo(x_i, y_i);
        }
        ctx.closePath();
        ctx.stroke();
      }
    }

    // Render embers
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
      ctx.fillStyle = 'hsla(' + p.hue + ', 100%, 60%, ' + p.life + ')';
      ctx.shadowColor = 'hsla(' + p.hue + ', 100%, 50%, 0.8)';
      ctx.shadowBlur = 4;
      ctx.fill();
      ctx.shadowBlur = 0;
    });

    win.requestAnimationFrame(drawEmbers);
  }
  drawEmbers();

  // ── Amber Cursor Glow ──────────────────────────────────────────────────────
  var g = doc.createElement('div');
  g.id = 'echo-cursor-glow';
  Object.assign(g.style, {
    position:'fixed', width:'260px', height:'260px', borderRadius:'50%',
    background:'radial-gradient(circle,rgba(245,158,11,0.06) 0%,rgba(239,68,68,0.02) 50%,transparent 70%)',
    pointerEvents:'none', zIndex:'9998', transform:'translate(-50%,-50%)',
    mixBlendMode:'screen', left:'-500px', top:'-500px'
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
