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

  // ── Matrix Digital Rain Canvas ─────────────────────────────────────────────
  var cvs = doc.createElement('canvas');
  cvs.id = 'theme-background-canvas';
  Object.assign(cvs.style, {
    position:'fixed', top:'0', left:'0', width:'100%', height:'100%',
    pointerEvents:'none', zIndex:'-1', opacity:'0.4'
  });
  doc.body.insertBefore(cvs, doc.body.firstChild);

  var ctx = cvs.getContext('2d');
  var W, H;
  
  function resize(){ W=cvs.width=win.innerWidth; H=cvs.height=win.innerHeight; }
  resize();
  win.addEventListener('resize', resize);

  // Digital Rain columns
  var fontSize = 14;
  var columns = Math.floor(win.innerWidth / fontSize) + 1;
  var drops = [];
  for (var i = 0; i < columns; i++) {
    drops[i] = Math.random() * -100; // start random height off screen
  }

  // Matrix characters
  var chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ";

  var active = true;
  var frameCount = 0;

  function drawMatrix() {
    if (!active || !doc.getElementById('theme-background-canvas')) {
      return;
    }
    
    // Slow down code rain slightly for high refresh rate screens
    frameCount++;
    if (frameCount % 2 !== 0) {
      win.requestAnimationFrame(drawMatrix);
      return;
    }

    // Semi-transparent black to create trailing fade effect
    ctx.fillStyle = 'rgba(0, 0, 0, 0.08)';
    ctx.fillRect(0, 0, W, H);

    ctx.fillStyle = '#00FF33';
    ctx.font = fontSize + 'px monospace';

    for (var i = 0; i < drops.length; i++) {
      var text = chars[Math.floor(Math.random() * chars.length)];
      var x = i * fontSize;
      var y = drops[i] * fontSize;

      // Draw the character
      ctx.fillText(text, x, y);

      // Reset when drop reaches bottom of screen
      if (y > H && Math.random() > 0.975) {
        drops[i] = 0;
      }
      drops[i]++;
    }

    win.requestAnimationFrame(drawMatrix);
  }
  drawMatrix();

  // ── Monospace Terminal Block Cursor ───────────────────────────────────────
  var g = doc.createElement('div');
  g.id = 'echo-cursor-glow';
  Object.assign(g.style, {
    position:'fixed', width:'12px', height:'22px',
    background:'#00FF33', boxShadow:'0 0 8px #00FF33',
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
    cx=lerp(cx,tx,0.2); cy=lerp(cy,ty,0.2);
    g.style.left=cx+'px'; g.style.top=cy+'px';
    win.requestAnimationFrame(loop);
  })();

  win.addEventListener('beforeunload', function() {
    active = false;
    runCursor = false;
  });
})();
