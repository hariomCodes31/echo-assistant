(function() {
  var doc = window.parent.document;
  var win = window.parent;

  // ── Clean up previous theme components ──
  var selectorsToClean = ['#neural-canvas', '#matrix-canvas', '#stars-canvas', '#theme-background-canvas', '#echo-cursor-glow', '.theme-bg-gradient'];
  selectorsToClean.forEach(function(sel) {
    var el = doc.querySelector(sel);
    if (el) { el.remove(); }
  });
  
  var oldStyle = doc.getElementById('theme-dynamic-bg-style');
  if (oldStyle) { oldStyle.remove(); }

  // ── Vision Frosted Blobs Canvas ──────────────────────────────────────────
  var cvs = doc.createElement('canvas');
  cvs.id = 'theme-background-canvas';
  Object.assign(cvs.style, {
    position:'fixed', top:'0', left:'0', width:'100%', height:'100%',
    pointerEvents:'none', zIndex:'-1', opacity:'0.75'
  });
  doc.body.insertBefore(cvs, doc.body.firstChild);

  var ctx = cvs.getContext('2d');
  var W, H;
  
  function resize(){ W=cvs.width=win.innerWidth; H=cvs.height=win.innerHeight; }
  resize();
  win.addEventListener('resize', resize);

  // Generate 4 large blobs floating in the background
  var blobs = [
    { x: W * 0.2, y: H * 0.3, r: 350, vx: 0.15, vy: 0.1,  color: 'rgba(255, 255, 255, 0.022)' },
    { x: W * 0.7, y: H * 0.2, r: 400, vx: -0.1,  vy: 0.15, color: 'rgba(255, 255, 255, 0.018)' },
    { x: W * 0.4, y: H * 0.7, r: 450, vx: 0.08, vy: -0.1, color: 'rgba(255, 255, 255, 0.025)' },
    { x: W * 0.8, y: H * 0.8, r: 300, vx: -0.12, vy: -0.08, color: 'rgba(255, 255, 255, 0.02)' }
  ];

  var active = true;

  function drawBlobs() {
    if (!active || !doc.getElementById('theme-background-canvas')) {
      return;
    }
    ctx.clearRect(0, 0, W, H);
    
    // Fill deep dark blue/gray base
    ctx.fillStyle = '#0a0b0e';
    ctx.fillRect(0, 0, W, H);

    blobs.forEach(function(b) {
      b.x += b.vx;
      b.y += b.vy;

      // Bounce
      if (b.x - b.r < 0 || b.x + b.r > W) b.vx *= -1;
      if (b.y - b.r < 0 || b.y + b.r > H) b.vy *= -1;

      // Draw soft gradient blob
      var grad = ctx.createRadialGradient(b.x, b.y, 0, b.x, b.y, b.r);
      grad.addColorStop(0, b.color);
      grad.addColorStop(0.5, 'rgba(255, 255, 255, 0.005)');
      grad.addColorStop(1, 'transparent');
      
      ctx.beginPath();
      ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
      ctx.fillStyle = grad;
      ctx.fill();
    });

    win.requestAnimationFrame(drawBlobs);
  }
  drawBlobs();

  // ── Soft White Cursor Glow ────────────────────────────────────────────────
  var g = doc.createElement('div');
  g.id = 'echo-cursor-glow';
  Object.assign(g.style, {
    position:'fixed', width:'240px', height:'240px', borderRadius:'50%',
    background:'radial-gradient(circle,rgba(255,255,255,0.06) 0%,rgba(255,255,255,0.015) 50%,transparent 70%)',
    pointerEvents:'none', zIndex:'9998', transform:'translate(-50%,-50%)',
    mixBlendMode:'screen', left:'-500px', top:'-500px',
    transition: 'transform 0.1s ease'
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

  // Listen for navigation/unloads to release listeners
  win.addEventListener('beforeunload', function() {
    active = false;
    runCursor = false;
  });
})();
