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

  // ── Neural Network Canvas Background ──────────────────────────────────────
  var cvs = doc.createElement('canvas');
  cvs.id = 'theme-background-canvas';
  Object.assign(cvs.style, {
    position:'fixed', top:'0', left:'0', width:'100%', height:'100%',
    pointerEvents:'none', zIndex:'-1', opacity:'0.55'
  });
  doc.body.insertBefore(cvs, doc.body.firstChild);

  var ctx = cvs.getContext('2d');
  var W, H, nodes = [], NODES=75, LINK=150;
  var mx=0, my=0;

  function resize(){ W=cvs.width=win.innerWidth; H=cvs.height=win.innerHeight; }
  resize();
  win.addEventListener('resize', resize);
  
  var moveListener = function(e){ mx=e.clientX; my=e.clientY; };
  doc.addEventListener('mousemove', moveListener);

  function mkNode(){
    return {
      x:Math.random()*W, y:Math.random()*H,
      vx:(Math.random()-0.5)*0.3,
      vy:(Math.random()-0.5)*0.3,
      hue: Math.random() < 0.6 ? 260 : 210 // Purple (260) or Blue (210)
    };
  }
  for(var i=0;i<NODES;i++) nodes.push(mkNode());

  var active = true;

  function drawNeural() {
    if (!active || !doc.getElementById('theme-background-canvas')) {
      doc.removeEventListener('mousemove', moveListener);
      return;
    }
    ctx.clearRect(0, 0, W, H);
    
    // Base dark purple void
    ctx.fillStyle = '#080313';
    ctx.fillRect(0, 0, W, H);

    // Update nodes
    var inf = 100;
    for(var i=0;i<nodes.length;i++){
      var n=nodes[i];
      var dx=n.x-mx, dy=n.y-my;
      var d=Math.sqrt(dx*dx+dy*dy);
      if(d<inf){ n.vx+=dx/d*0.03; n.vy+=dy/d*0.03; }
      n.x+=n.vx; n.y+=n.vy;
      n.vx*=0.97; n.vy*=0.97;
      if(n.x<0||n.x>W) n.vx*=-1;
      if(n.y<0||n.y>H) n.vy*=-1;
    }

    // Draw links
    for(var i=0;i<nodes.length;i++){
      for(var j=i+1;j<nodes.length;j++){
        var dx=nodes[i].x-nodes[j].x, dy=nodes[i].y-nodes[j].y;
        var dist=Math.sqrt(dx*dx+dy*dy);
        if(dist<LINK){
          var alpha=(1-dist/LINK)*0.15;
          ctx.beginPath();
          ctx.moveTo(nodes[i].x,nodes[i].y);
          ctx.lineTo(nodes[j].x,nodes[j].y);
          ctx.strokeStyle='rgba(139, 92, 246,'+alpha+')';
          ctx.lineWidth=0.7;
          ctx.stroke();
        }
      }
    }

    // Draw nodes
    for(var i=0;i<nodes.length;i++){
      var n=nodes[i];
      ctx.beginPath();
      ctx.arc(n.x,n.y,2.5,0,Math.PI*2);
      ctx.fillStyle='hsla('+n.hue+',100%,65%,0.6)';
      ctx.fill();
    }
    
    win.requestAnimationFrame(drawNeural);
  }
  drawNeural();

  // ── Purple Cursor Glow ───────────────────────────────────────────────────
  var g = doc.createElement('div');
  g.id = 'echo-cursor-glow';
  Object.assign(g.style, {
    position:'fixed', width:'280px', height:'280px', borderRadius:'50%',
    background:'radial-gradient(circle,rgba(139,92,246,0.06) 0%,rgba(59,130,246,0.02) 50%,transparent 70%)',
    pointerEvents:'none', zIndex:'9998', transform:'translate(-50%,-50%)',
    mixBlendMode:'screen', left:'-500px', top:'-500px'
  });
  doc.body.appendChild(g);

  var cx=win.innerWidth/2, cy=win.innerHeight/2, tx=cx, ty=cy;
  function lerp(a,b,t){ return a+(b-a)*t; }
  
  var cursorMoveListener = function(e){ tx=e.clientX; ty=e.clientY; };
  doc.addEventListener('mousemove', cursorMoveListener);
  
  var runCursor = true;
  (function loop(){
    if (!runCursor || !doc.getElementById('echo-cursor-glow')) {
      doc.removeEventListener('mousemove', cursorMoveListener);
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
