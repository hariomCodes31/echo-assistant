(function() {
  var doc = window.parent.document;
  var win = window.parent;

  // ── Clean up any existing theme canvases/elements ──
  var selectorsToClean = ['#neural-canvas', '#matrix-canvas', '#stars-canvas', '#theme-background-canvas', '#echo-cursor-glow', '.theme-bg-gradient'];
  selectorsToClean.forEach(function(sel) {
    var el = doc.querySelector(sel);
    if (el) { el.remove(); }
  });
  
  // Also clean up any inline custom styling elements that might have been added
  var oldStyle = doc.getElementById('theme-dynamic-bg-style');
  if (oldStyle) { oldStyle.remove(); }

  // ── Neural network canvas background ──────────────────────────────────────
  var cvs = doc.createElement('canvas');
  cvs.id = 'neural-canvas';
  Object.assign(cvs.style, {
    position:'fixed', top:'0', left:'0', width:'100%', height:'100%',
    pointerEvents:'none', zIndex:'-1', opacity:'0.55'
  });
  doc.body.insertBefore(cvs, doc.body.firstChild);

  var ctx = cvs.getContext('2d');
  var W, H, nodes = [], NODES=80, LINK=160;
  var mx=0, my=0;

  function resize(){ W=cvs.width=win.innerWidth; H=cvs.height=win.innerHeight; }
  resize();
  win.addEventListener('resize', resize);
  
  var moveListener = function(e){ mx=e.clientX; my=e.clientY; };
  doc.addEventListener('mousemove', moveListener);

  function mkNode(){
    return {
      x:Math.random()*W, y:Math.random()*H,
      z:Math.random()*400,
      vx:(Math.random()-0.5)*0.25,
      vy:(Math.random()-0.5)*0.25,
      vz:(Math.random()-0.5)*0.5,
      hue: Math.random()<0.6 ? 193 : (Math.random()<0.5 ? 260 : 330)
    };
  }
  for(var i=0;i<NODES;i++) nodes.push(mkNode());

  var frame=0;
  var active = true;

  function drawNeural(){
    if (!active || !doc.getElementById('neural-canvas')) {
      doc.removeEventListener('mousemove', moveListener);
      return;
    }
    frame++;
    ctx.clearRect(0,0,W,H);

    // ── Draw links from AI Core to surrounding panels ──────────────────────
    var coreIframe = doc.querySelector('iframe[title="components.ai_core.render_ai_core"]');
    if (coreIframe) {
      var rCore = coreIframe.getBoundingClientRect();
      var coreX = rCore.left + rCore.width / 2;
      var coreY = rCore.top + rCore.height / 2;

      var panels = doc.querySelectorAll('[data-testid="stVerticalBlockBorderWrapper"]');
      panels.forEach(function(p) {
        if (p.contains(coreIframe)) return;
        
        var rPanel = p.getBoundingClientRect();
        var px = rPanel.left + rPanel.width / 2;
        var py = rPanel.top + rPanel.height / 2;

        ctx.beginPath();
        ctx.moveTo(coreX, coreY);
        ctx.lineTo(px, py);
        ctx.strokeStyle = 'rgba(0, 217, 255, 0.085)';
        ctx.lineWidth = 1;
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(coreX, coreY);
        ctx.lineTo(px, py);
        ctx.strokeStyle = 'rgba(123, 97, 255, 0.03)';
        ctx.lineWidth = 3;
        ctx.stroke();

        var flowSpd = 0.005;
        var progress = (frame * flowSpd) % 1.0;
        var nx = coreX + (px - coreX) * progress;
        var ny = coreY + (py - coreY) * progress;

        ctx.beginPath();
        ctx.arc(nx, ny, 2.5, 0, Math.PI*2);
        ctx.fillStyle = '#00d9ff';
        ctx.shadowColor = '#00d9ff';
        ctx.shadowBlur = 6;
        ctx.fill();
        ctx.shadowBlur = 0; // reset
      });
    }

    // Cursor influence
    var inf = 80;
    for(var i=0;i<nodes.length;i++){
      var n=nodes[i];
      var dx=n.x-mx, dy=n.y-my;
      var d=Math.sqrt(dx*dx+dy*dy);
      if(d<inf){ n.vx+=dx/d*0.04; n.vy+=dy/d*0.04; }
      n.x+=n.vx; n.y+=n.vy; n.z+=n.vz;
      n.vx*=0.98; n.vy*=0.98;
      if(n.x<0||n.x>W) n.vx*=-1;
      if(n.y<0||n.y>H) n.vy*=-1;
      if(n.z<0||n.z>400) n.vz*=-1;
    }

    // Draw links
    for(var i=0;i<nodes.length;i++){
      for(var j=i+1;j<nodes.length;j++){
        var dx=nodes[i].x-nodes[j].x, dy=nodes[i].y-nodes[j].y;
        var dist=Math.sqrt(dx*dx+dy*dy);
        if(dist<LINK){
          var alpha=(1-dist/LINK)*0.12*(nodes[i].z/400+0.2);
          ctx.beginPath();
          ctx.moveTo(nodes[i].x,nodes[i].y);
          ctx.lineTo(nodes[j].x,nodes[j].y);
          ctx.strokeStyle='rgba(0,217,255,'+alpha+')';
          ctx.lineWidth=0.6;
          ctx.stroke();
        }
      }
    }

    // Draw nodes
    for(var i=0;i<nodes.length;i++){
      var n=nodes[i];
      var depth=(n.z/400);
      var r=1+depth*2.5;
      var alpha=0.3+depth*0.6;
      ctx.beginPath();
      ctx.arc(n.x,n.y,r,0,Math.PI*2);
      ctx.fillStyle='hsla('+n.hue+',100%,65%,'+alpha+')';
      ctx.fill();
      if(depth>0.5){
        var g=ctx.createRadialGradient(n.x,n.y,0,n.x,n.y,r*5);
        g.addColorStop(0,'hsla('+n.hue+',100%,65%,0.25)');
        g.addColorStop(1,'transparent');
        ctx.beginPath(); ctx.arc(n.x,n.y,r*5,0,Math.PI*2);
        ctx.fillStyle=g; ctx.fill();
      }
    }
    win.requestAnimationFrame(drawNeural);
  }
  drawNeural();

  // ── Cursor glow ───────────────────────────────────────────────────────────
  var g = doc.createElement('div');
  g.id = 'echo-cursor-glow';
  Object.assign(g.style, {
    position:'fixed', width:'280px', height:'280px', borderRadius:'50%',
    background:'radial-gradient(circle,rgba(0,217,255,0.055) 0%,rgba(123,97,255,0.025) 45%,transparent 70%)',
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

  // Listen for navigation/unloads to release listeners
  win.addEventListener('beforeunload', function() {
    active = false;
    runCursor = false;
  });
})();
