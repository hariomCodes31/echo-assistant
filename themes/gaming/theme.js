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

  // ── Gaming RGB Canvas Background ──────────────────────────────────────────
  var cvs = doc.createElement('canvas');
  cvs.id = 'theme-background-canvas';
  Object.assign(cvs.style, {
    position:'fixed', top:'0', left:'0', width:'100%', height:'100%',
    pointerEvents:'none', zIndex:'-1', opacity:'0.3'
  });
  doc.body.insertBefore(cvs, doc.body.firstChild);

  var ctx = cvs.getContext('2d');
  var W, H;
  
  function resize(){ W=cvs.width=win.innerWidth; H=cvs.height=win.innerHeight; }
  resize();
  win.addEventListener('resize', resize);

  var active = true;
  var hueShift = 0;

  function drawRGB() {
    if (!active || !doc.getElementById('theme-background-canvas')) {
      return;
    }
    ctx.clearRect(0, 0, W, H);
    
    // Base dark gray
    ctx.fillStyle = '#05070a';
    ctx.fillRect(0, 0, W, H);

    hueShift = (hueShift + 0.5) % 360;

    // Draw RGB accent line on bottom of horizon
    ctx.beginPath();
    ctx.moveTo(0, H - 2);
    ctx.lineTo(W, H - 2);
    ctx.strokeStyle = 'hsla(' + hueShift + ', 100%, 50%, 0.8)';
    ctx.lineWidth = 4;
    ctx.stroke();

    // Draw carbon geometric patterns
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.008)';
    ctx.lineWidth = 1;
    var size = 30;
    for (var x = 0; x < W; x += size) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x + size, H);
      ctx.stroke();
    }

    win.requestAnimationFrame(drawRGB);
  }
  drawRGB();

  // ── RGB Cursor Glow ────────────────────────────────────────────────────────
  var g = doc.createElement('div');
  g.id = 'echo-cursor-glow';
  Object.assign(g.style, {
    position:'fixed', width:'220px', height:'220px', borderRadius:'50%',
    background:'radial-gradient(circle,rgba(0,255,0,0.06) 0%,transparent 65%)',
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
    
    // Cycle cursor color
    var cursorHue = (Date.now() * 0.1) % 360;
    g.style.background = 'radial-gradient(circle, hsla(' + cursorHue + ', 100%, 50%, 0.06) 0%, transparent 65%)';

    g.style.left=cx+'px'; g.style.top=cy+'px';
    win.requestAnimationFrame(loop);
  })();

  win.addEventListener('beforeunload', function() {
    active = false;
    runCursor = false;
  });
})();
