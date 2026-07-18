(function() {
  var doc = window.parent.document;
  var win = window.parent;

  // Cleanup all custom visual canvas or cursors
  var selectorsToClean = ['#neural-canvas', '#matrix-canvas', '#stars-canvas', '#theme-background-canvas', '#echo-cursor-glow', '.theme-bg-gradient'];
  selectorsToClean.forEach(function(sel) {
    var el = doc.querySelector(sel);
    if (el) { el.remove(); }
  });
  
  var oldStyle = doc.getElementById('theme-dynamic-bg-style');
  if (oldStyle) { oldStyle.remove(); }

  // Inject a solid static backdrop color just in case
  var style = doc.createElement('style');
  style.id = 'theme-dynamic-bg-style';
  style.textContent = 'body { background-color: #0a0a0a !important; }';
  doc.head.appendChild(style);
})();
