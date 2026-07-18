(function() {
  var doc = window.parent.document;
  var win = window.parent;

  // Cleanup
  var selectorsToClean = ['#neural-canvas', '#matrix-canvas', '#stars-canvas', '#theme-background-canvas', '#echo-cursor-glow', '.theme-bg-gradient'];
  selectorsToClean.forEach(function(sel) {
    var el = doc.querySelector(sel);
    if (el) { el.remove(); }
  });
  
  var oldStyle = doc.getElementById('theme-dynamic-bg-style');
  if (oldStyle) { oldStyle.remove(); }

  // ── Cyberpunk Grid Canvas ──────────────────────────────────────────────────
  var cvs = doc.createElement('canvas');
  cvs.id = 'theme-background-canvas';
  Object.assign(cvs.style, {
    position:'fixed', top:'0', left:'0', width:'100%', height:'100%',
    pointerEvents:'none', zIndex:'-1', opacity:'0.35'
  });
  doc.body.insertBefore(cvs, doc.body.firstChild);

  var ctx = cvs.getContext('2d');
  var W, H;
  
  function resize(){ W=cvs.width=win.innerWidth; H=cvs.height=win.innerHeight; }
  resize();
  win.addEventListener('resize', resize);

  var gridOffset = 0;
  var active = true;

  function drawGrid() {
    if (!active || !doc.getElementById('theme-background-canvas')) {
      return;
    }
    ctx.clearRect(0, 0, W, H);
    
    // Background void
    ctx.fillStyle = '#06020c';
    ctx.fillRect(0, 0, W, H);

    // Draw perspective neon grid lines on bottom half
    ctx.strokeStyle = 'rgba(255, 0, 119, 0.1)';
    ctx.lineWidth = 1;
    gridOffset = (gridOffset + 1.2) % 40;

    // Horizontal lines
    for (var y = H/2; y < H; y += 40) {
      ctx.beginPath();
      ctx.moveTo(0, y + (gridOffset % 40));
      ctx.lineTo(W, y + (gridOffset % 40));
      ctx.stroke();
    }

    // Vertical lines from center horizon outward
    var horizonY = H/2;
    var centerX = W/2;
    for (var x = -W; x < W * 2; x += 60) {
      ctx.beginPath();
      ctx.moveTo(centerX + (x - centerX) * 0.05, horizonY);
      ctx.lineTo(x, H);
      ctx.stroke();
    }

    // Dynamic horizontal scanline sweep
    var sweepY = (Date.now() * 0.15) % H;
    ctx.beginPath();
    ctx.moveTo(0, sweepY);
    ctx.lineTo(W, sweepY);
    ctx.strokeStyle = 'rgba(0, 255, 204, 0.12)';
    ctx.lineWidth = 2;
    ctx.stroke();

    win.requestAnimationFrame(drawGrid);
  }
  drawGrid();

  // ── Glitchy Cursor Glow (Cyan/Pink Flicker) ────────────────────────────────
  var g = doc.createElement('div');
  g.id = 'echo-cursor-glow';
  Object.assign(g.style, {
    position:'fixed', width:'240px', height:'240px', borderRadius:'50%',
    background:'radial-gradient(circle,rgba(255,0,119,0.06) 0%,rgba(0,255,204,0.03) 50%,transparent 70%)',
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
    cx=lerp(cx,tx,0.12); cy=lerp(cy,ty,0.12);
    
    // Add micro neon glitch flicker
    var randomFlicker = Math.random() < 0.15 ? 'rgba(0,255,204,0.08)' : 'rgba(255,0,119,0.06)';
    g.style.background = 'radial-gradient(circle,' + randomFlicker + ' 0%,rgba(0,255,204,0.02) 55%,transparent 70%)';

    g.style.left=cx+'px'; g.style.top=cy+'px';
    win.requestAnimationFrame(loop);
  })();

  win.addEventListener('beforeunload', function() {
    active = false;
    runCursor = false;
  });
})();
