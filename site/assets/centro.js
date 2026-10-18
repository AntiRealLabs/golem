/* Golem Bench · la cruz
   Se llega al centro, a la pregunta, y desde ahí se puede ir hacia todos los lados:
   arriba, lo que no sabemos; abajo, lo que nos sostiene; a la izquierda, lo que medimos;
   a la derecha, lo que guardamos.
   Sin este archivo la página sigue funcionando: cada sala tiene su enlace. */
(function () {
  'use strict';
  var d = document, w = window;
  var fila = d.getElementById('fila');
  var pregunta = d.getElementById('pregunta');
  var centro = d.getElementById('centro');
  if (!fila || !pregunta || !centro) return;

  var ORDEN = ['medimos', 'pregunta', 'guardamos'];   // orden visual de la fila
  var top = d.querySelector('.top');

  function reducir() {
    return w.matchMedia && w.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }
  function tipoDeLlegada() {
    var e = w.performance && performance.getEntriesByType ? performance.getEntriesByType('navigation')[0] : null;
    return e ? e.type : 'navigate';
  }
  function indiceFila() {
    return Math.max(0, Math.min(ORDEN.length - 1, Math.round(fila.scrollLeft / Math.max(1, fila.clientWidth))));
  }

  /* 1. Aterrizar en el centro: solo en una visita nueva y sin destino en la dirección.
        Si la persona vuelve atrás o recarga, el navegador recuerda dónde estaba. */
  var tocado = false;
  function aterrizar() {
    if (tocado) return;
    var destino = location.hash.slice(1);
    // la fila mira a la pregunta salvo que el enlace pida una de sus salas laterales
    if (destino !== 'medimos' && destino !== 'guardamos') fila.scrollLeft = pregunta.offsetLeft;
    if (destino || tipoDeLlegada() !== 'navigate') return;
    var y = centro.getBoundingClientRect().top + w.pageYOffset - (top ? top.offsetHeight : 0);
    w.scrollTo({ top: Math.max(0, y), left: 0, behavior: 'instant' });
  }
  aterrizar();
  ['wheel', 'touchstart', 'keydown', 'pointerdown'].forEach(function (ev) {
    w.addEventListener(ev, function () { tocado = true; }, { passive: true, once: true });
  });
  // las letras y las imágenes pueden mover un poco el centro mientras cargan
  if (d.fonts && d.fonts.ready) d.fonts.ready.then(aterrizar);
  w.addEventListener('load', aterrizar);

  /* 2. La brújula dice dónde estás. */
  var puntos = Array.prototype.slice.call(d.querySelectorAll('.brujula .b'));
  var actual = null;
  function sala() {
    var mitad = w.innerHeight / 2;
    var r = centro.getBoundingClientRect();
    if (r.top <= mitad && r.bottom >= mitad) return ORDEN[indiceFila()];
    return r.top > mitad ? 'arriba' : 'abajo';
  }
  function marcar() {
    pendiente = false;
    var s = sala();
    if (s === actual) return;
    actual = s;
    puntos.forEach(function (a) {
      if (a.getAttribute('data-sala') === s) a.setAttribute('aria-current', 'location');
      else a.removeAttribute('aria-current');
    });
    d.documentElement.setAttribute('data-sala', s);
  }
  var pendiente = false;
  function pedir() {
    if (!pendiente) { pendiente = true; w.requestAnimationFrame(marcar); }
  }
  w.addEventListener('scroll', pedir, { passive: true });
  fila.addEventListener('scroll', pedir, { passive: true });
  marcar();

  // si cambia el tamaño de la ventana (girar el teléfono), la fila se queda en la misma sala
  var salaFila = indiceFila(), anchoFila = fila.clientWidth;
  fila.addEventListener('scroll', function () {
    if (fila.clientWidth === anchoFila) salaFila = indiceFila();
  }, { passive: true });
  w.addEventListener('resize', function () {
    if (fila.clientWidth !== anchoFila || Math.abs(fila.scrollLeft - salaFila * fila.clientWidth) > 2) {
      anchoFila = fila.clientWidth;
      fila.scrollLeft = salaFila * fila.clientWidth;
    }
    pedir();
  });

  /* 3. Los enlaces a las salas de la fila mueven los dos ejes a la vez:
        la página baja o sube hasta la fila, y la fila se desliza hacia el lado. */
  function irA(destino, como) {
    var i = ORDEN.indexOf(destino);
    if (i === -1) return false;
    var y = centro.getBoundingClientRect().top + w.pageYOffset - (top ? top.offsetHeight : 0);
    w.scrollTo({ top: Math.max(0, y), left: 0, behavior: como });
    fila.scrollTo({ left: i * fila.clientWidth, behavior: como });
    return true;
  }
  d.addEventListener('click', function (e) {
    var a = e.target.closest ? e.target.closest('a[href^="#"]') : null;
    if (!a || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var destino = a.getAttribute('href').slice(1);
    if (ORDEN.indexOf(destino) === -1) return;
    e.preventDefault();
    tocado = true;
    irA(destino, reducir() ? 'instant' : 'smooth');
    if (location.hash !== '#' + destino) history.pushState(null, '', '#' + destino);
    var sala = d.getElementById(destino);
    if (sala && sala.focus) sala.focus({ preventScroll: true });
  });
  w.addEventListener('popstate', function () {
    var destino = location.hash.slice(1) || 'pregunta';
    if (ORDEN.indexOf(destino) !== -1) fila.scrollTo({ left: ORDEN.indexOf(destino) * fila.clientWidth, behavior: 'instant' });
  });
  w.addEventListener('hashchange', function () { irA(location.hash.slice(1), 'instant'); });
  if (ORDEN.indexOf(location.hash.slice(1)) !== -1) irA(location.hash.slice(1), 'instant');

  /* 4. Con el teclado: ← y → recorren la fila del centro cuando está a la vista. */
  d.addEventListener('keydown', function (e) {
    if (e.defaultPrevented || e.altKey || e.ctrlKey || e.metaKey || e.shiftKey) return;
    if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
    var t = e.target;
    if (t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName))) return;
    var r = centro.getBoundingClientRect();
    if (r.bottom < w.innerHeight * 0.35 || r.top > w.innerHeight * 0.65) return;
    var i = indiceFila() + (e.key === 'ArrowRight' ? 1 : -1);
    if (i < 0 || i >= ORDEN.length) return;
    e.preventDefault();
    fila.scrollTo({ left: i * fila.clientWidth, behavior: reducir() ? 'instant' : 'smooth' });
  });
})();
