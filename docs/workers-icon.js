/* HAMSE - Workers home-screen icon (iPhone style) */
(function () {
  'use strict';
  var KEY = 'hamse_icpos_w', ov = null, fr = null, el = null;

  var st = document.createElement('style');
  st.textContent =
    '#hwv{position:fixed;inset:0;z-index:99990;background:#000;opacity:0;transform:scale(.2);border-radius:36px;overflow:hidden;pointer-events:none;transition:opacity .25s ease,transform .38s cubic-bezier(.2,.9,.25,1),border-radius .38s ease}' +
    '#hwv.open{opacity:1;transform:none;border-radius:0;pointer-events:auto}' +
    '#hwv iframe{width:100%;height:100%;border:0;background:#000;display:block}';
  document.head.appendChild(st);

  function close() { if (ov) ov.classList.remove('open'); }
  window.addEventListener('message', function (e) { if (e.data === 'hamse-close') close(); });

  function open() {
    if (!ov) {
      ov = document.createElement('div'); ov.id = 'hwv';
      fr = document.createElement('iframe'); fr.src = 'workers.html'; fr.title = 'Workers';
      ov.appendChild(fr); document.body.appendChild(ov);
      fr.addEventListener('load', function () {
        try { var b = fr.contentDocument.getElementById('bk'); if (b) b.onclick = close; } catch (e) {}
      });
    }
    var r = el.getBoundingClientRect();
    ov.style.transformOrigin = (r.left + r.width / 2) + 'px ' + (r.top + r.height / 2) + 'px';
    void ov.offsetWidth;
    ov.classList.add('open');
  }

  function save() {
    var par = el.offsetParent || el.parentNode;
    try { localStorage.setItem(KEY, JSON.stringify({ px: el.offsetLeft / par.clientWidth, py: el.offsetTop / par.clientHeight })); } catch (e) {}
  }

  function place(orig, par) {
    var W = par.clientWidth, H = par.clientHeight, w = el.offsetWidth, h = el.offsetHeight, s = null, x, y;
    try { s = JSON.parse(localStorage.getItem(KEY) || 'null'); } catch (e) {}
    if (s && typeof s.px === 'number') { x = s.px * W; y = s.py * H; }
    else {
      x = orig.offsetLeft + orig.offsetWidth + 24; y = orig.offsetTop;
      if (x + w > W - 8) { x = orig.offsetLeft; y = orig.offsetTop + orig.offsetHeight + 24; }
    }
    x = Math.max(0, Math.min(W - w, x)); y = Math.max(0, Math.min(H - h, y));
    el.style.left = x + 'px'; el.style.top = y + 'px';
  }
  function tryPlace(orig) {
    var par = el.offsetParent;
    if (!par || !par.clientWidth || !orig.offsetWidth) { setTimeout(function () { tryPlace(orig); }, 400); return; }
    place(orig, par);
  }

  function drag() {
    var sx, sy, ox, oy, moving = false, down = false;
    el.addEventListener('click', function (e) { e.stopPropagation(); e.preventDefault(); }, true);
    el.addEventListener('pointerdown', function (e) {
      down = true; moving = false; sx = e.clientX; sy = e.clientY; ox = el.offsetLeft; oy = el.offsetTop;
      el.style.transform = 'scale(.92)';
      try { el.setPointerCapture(e.pointerId); } catch (x) {}
    });
    el.addEventListener('pointermove', function (e) {
      if (!down) return;
      var dx = e.clientX - sx, dy = e.clientY - sy;
      if (!moving && Math.sqrt(dx * dx + dy * dy) < 10) return;
      moving = true; el.style.transform = 'none';
      var par = el.offsetParent || el.parentNode;
      el.style.left = Math.max(0, Math.min(par.clientWidth - el.offsetWidth, ox + dx)) + 'px';
      el.style.top = Math.max(0, Math.min(par.clientHeight - el.offsetHeight, oy + dy)) + 'px';
    });
    function end(e) {
      if (!down) return;
      down = false; el.style.transform = 'none';
      if (moving) save(); else if (e.type === 'pointerup') open();
    }
    el.addEventListener('pointerup', end);
    el.addEventListener('pointercancel', end);
  }

  function build(orig) {
    el = orig.cloneNode(true);
    var all = [el].concat([].slice.call(el.querySelectorAll('*')));
    all.forEach(function (n) {
      n.removeAttribute('id'); n.removeAttribute('onclick');
      [].slice.call(n.attributes).forEach(function (a) { if (/^data-/.test(a.name)) n.removeAttribute(a.name); });
    });
    var b = el.querySelector('b') || el.firstElementChild;
    if (b) {
      b.style.background = 'linear-gradient(135deg,#ff9f0a,#ff375f)';
      b.style.display = 'flex'; b.style.alignItems = 'center'; b.style.justifyContent = 'center';
      b.innerHTML = '<svg viewBox="0 0 24 24" style="width:54%;height:54%" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 7l-5 5 5 5"/><path d="M16 7l5 5-5 5"/><path d="M13.5 5l-3 14"/></svg>';
    }
    var tw = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null), n;
    while ((n = tw.nextNode())) { if (n.data.trim()) { n.data = 'Workers'; break; } }
    el.style.position = 'absolute'; el.style.transform = 'none'; el.style.right = 'auto'; el.style.bottom = 'auto'; el.style.margin = '0';
    el.style.touchAction = 'none'; el.style.userSelect = 'none'; el.style.webkitUserSelect = 'none';
    orig.parentNode.appendChild(el);
    tryPlace(orig);
    drag();
  }

  var t = setInterval(function () {
    if (el) { clearInterval(t); return; }
    var orig = document.querySelector('#home > .ic') || document.querySelector('#grid .ic');
    if (orig) { clearInterval(t); build(orig); }
  }, 400);
})();
