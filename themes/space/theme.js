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

  // ── Starfield Canvas Background ───────────────────────────────────────────
  var cvs = doc.createElement('canvas');
  cvs.id = 'theme-background-canvas';
  Object.assign(cvs.style, {
    position:'fixed', top:'0', left:'0', width:'100%', height:'100%',
    pointerEvents:'none', zIndex:'-1', opacity:'0.6'
  });
  doc.body.insertBefore(cvs, doc.body.firstChild);

  var ctx = cvs.getContext('2d');
  var W, H;
  
  function resize(){ W=cvs.width=win.innerWidth; H=cvs.height=win.innerHeight; }
  resize();
  win.addEventListener('resize', resize);

  var stars = [];
  var NUM_STARS = 100;

  function mkStar() {
    return {
      x: Math.random() * W,
      y: Math.random() * H,
      r: 0.5 + Math.random() * 1.5,
      alpha: 0.2 + Math.random() * 0.8,
      speed: 0.05 + Math.random() * 0.1
    };
  }

  for (var i = 0; i < NUM_STARS; i++) {
    stars.push(mkStar());
  }

  var active = true;

  function drawStars() {
    if (!active || !doc.getElementById('theme-background-canvas')) {
      return;
    }
    ctx.clearRect(0, 0, W, H);
    
    // Deep space dark background
    ctx.fillStyle = '#020308';
    ctx.fillRect(0, 0, W, H);

    // Draw grid coordinates in background
    ctx.strokeStyle = 'rgba(59, 130, 246, 0.015)';
    ctx.lineWidth = 1;
    var gridSize = 80;
    for (var x = 0; x < W; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, H);
      ctx.stroke();
    }
    for (var y = 0; y < H; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(W, y);
      ctx.stroke();
    }

    // Render stars
    ctx.fillStyle = '#ffffff';
    stars.forEach(function(s) {
      s.x -= s.speed;
      if (s.x < 0) {
        s.x = W;
        s.y = Math.random() * H;
      }
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(255, 255, 255, ' + s.alpha + ')';
      ctx.fill();
    });

    win.requestAnimationFrame(drawStars);
  }
  drawStars();

  // ── Radar Circular Cursor Glow ────────────────────────────────────────────
  var g = doc.createElement('div');
  g.id = 'echo-cursor-glow';
  Object.assign(g.style, {
    position:'fixed', width:'180px', height:'180px', borderRadius:'50%',
    border:'1px solid rgba(59,130,246,0.15)',
    background:'radial-gradient(circle,rgba(59,130,246,0.04) 0%,transparent 65%)',
    pointerEvents:'none', zIndex:'9998', transform:'translate(-50%,-50%)',
    left:'-500px', top:'-500px'
  });
  doc.body.appendChild(g);

  // Add target crosshairs inside radar cursor
  var crossX = doc.createElement('div');
  Object.assign(crossX.style, {
    position: 'absolute', top: '50%', left: '0', width: '100%', height: '1px',
    background: 'rgba(59, 130, 246, 0.1)', transform: 'translateY(-50%)'
  });
  var crossY = doc.createElement('div');
  Object.assign(crossY.style, {
    position: 'absolute', left: '50%', top: '0', height: '100%', width: '1px',
    background: 'rgba(59, 130, 246, 0.1)', transform: 'translateX(-50%)'
  });
  g.appendChild(crossX);
  g.appendChild(crossY);

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
