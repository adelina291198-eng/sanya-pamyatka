(function () {
  'use strict';
  var TRIP = { y: 2026, m: 11, d0: 4, d1: 13 }; // 4–13 декабря 2026 (месяц с нуля)

  // ---------- Вкладки ----------
  var tabs = [].slice.call(document.querySelectorAll('nav.tabs a'));
  var scrollPos = {};
  var current = null;
  function show(hash) {
    var h = (hash || '').replace(/^#/, '').split('/');
    var tab = h[0], anchor = h[1];
    if (!document.getElementById('p-' + tab)) { // ссылка на карточку: #yanoda
      var el = tab && document.getElementById(tab), pane = el && el.closest('.pane');
      if (pane) { anchor = tab; tab = pane.id.slice(2); } else tab = 'home';
    }
    if (current) scrollPos[current] = window.scrollY;
    tabs.forEach(function (a) { a.classList.toggle('on', a.dataset.tab === tab); });
    [].forEach.call(document.querySelectorAll('.pane'), function (p) { p.hidden = p.id !== 'p-' + tab; });
    var changed = current !== tab; current = tab;
    if (anchor && document.getElementById(anchor)) document.getElementById(anchor).scrollIntoView();
    else if (changed) window.scrollTo(0, scrollPos[tab] || 0);
  }
  window.addEventListener('hashchange', function () { show(location.hash); });
  show(location.hash);
  // повторное нажатие на открытую вкладку — наверх
  tabs.forEach(function (a) {
    a.addEventListener('click', function (e) {
      if (a.dataset.tab === current && location.hash.split('/')[0] === '#' + current) { e.preventDefault(); window.scrollTo(0, 0); }
    });
  });

  // ---------- Копировать / Показать крупно ----------
  function copyText(t, btn) {
    function ok() {
      var o = btn.textContent; btn.textContent = 'Скопировано ✓'; btn.classList.add('done');
      setTimeout(function () { btn.textContent = o; btn.classList.remove('done'); }, 1800);
    }
    function fallback() {
      var ta = document.createElement('textarea'); ta.value = t; ta.style.position = 'fixed'; ta.style.opacity = '0';
      document.body.appendChild(ta); ta.focus(); ta.select();
      try { document.execCommand('copy'); ok(); } catch (e) { alert(t); }
      document.body.removeChild(ta);
    }
    try { if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(t).then(ok, fallback); else fallback(); }
    catch (e) { fallback(); }
  }
  var big = document.getElementById('big'), bigtxt = document.getElementById('bigtxt');
  document.addEventListener('click', function (e) {
    var b = e.target.closest('button.cp, button.qb'); if (!b) return;
    if (b.dataset.show) { bigtxt.innerHTML = b.dataset.show; big.classList.add('on'); return; }
    if (b.dataset.t) copyText(b.dataset.t, b);
  });
  document.getElementById('bigclose').addEventListener('click', function () { big.classList.remove('on'); });

  // ---------- Сегодня ----------
  function sanyaToday() { // дата в Санье (UTC+8)
    var n = new Date(Date.now() + 8 * 3600e3);
    return new Date(Date.UTC(n.getUTCFullYear(), n.getUTCMonth(), n.getUTCDate()));
  }
  var planItems = [].slice.call(document.querySelectorAll('#p-home h2#plan ~ .card li'));
  var byDay = {};
  planItems.forEach(function (li) { var m = /^\s*(\d+)\s+дек/.exec(li.textContent); if (m && !byDay[m[1]]) byDay[m[1]] = li; });
  var t = sanyaToday(), start = Date.UTC(TRIP.y, TRIP.m, TRIP.d0), end = Date.UTC(TRIP.y, TRIP.m, TRIP.d1);
  var box = document.getElementById('today'), html;
  if (t < start) {
    var days = Math.round((start - t) / 864e5);
    html = '<div class="lbl">До поездки ' + days + ' ' + plural(days, 'день', 'дня', 'дней') + '</div>' +
      '<div class="txt">Первый день:</div><ul><li>' + (byDay[TRIP.d0] ? byDay[TRIP.d0].innerHTML : '') + '</li></ul>';
  } else if (t <= end) {
    var d = new Date(t).getUTCDate(), li = byDay[d];
    if (li) li.classList.add('now');
    html = '<div class="lbl">Сегодня в Санье</div><ul><li>' + (li ? li.innerHTML : 'Отдых') + '</li></ul>' +
      (byDay[d + 1] ? '<div class="txt small">Завтра: ' + byDay[d + 1].innerHTML + '</div>' : '');
  } else {
    html = '<div class="lbl">Поездка закончилась</div><div class="txt">С возвращением! 🌴</div>';
  }
  box.innerHTML = html;
  function plural(n, a, b, c) { var m10 = n % 10, m100 = n % 100; return m10 === 1 && m100 !== 11 ? a : (m10 >= 2 && m10 <= 4 && (m100 < 10 || m100 >= 20) ? b : c); }

  // ---------- Отметка «Были» ----------
  var KEY = 'sanya-been';
  var been = {};
  try { been = JSON.parse(localStorage.getItem(KEY) || '{}') || {}; } catch (e) { been = {}; }
  function save() { try { localStorage.setItem(KEY, JSON.stringify(been)); } catch (e) {} }
  [].forEach.call(document.querySelectorAll('#p-home .card.place, #p-places .card, #p-food .card, #p-shop .card'), function (card) {
    var h = card.querySelector('h3'); if (!h) return;
    var id = h.textContent.trim();
    var btn = document.createElement('button'); btn.type = 'button'; btn.className = 'been';
    function paint() { var on = !!been[id]; btn.classList.toggle('on', on); card.classList.toggle('was', on); btn.textContent = on ? '✓ Были здесь' : '☐ Отметить: были'; }
    btn.addEventListener('click', function () { if (been[id]) delete been[id]; else been[id] = 1; save(); paint(); });
    paint(); card.appendChild(btn);
  });

  // ---------- Работа без интернета ----------
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () { navigator.serviceWorker.register('sw.js').catch(function () {}); });
  }
})();
