/* Golem Bench · el archivo de ED01
   Atiende tres cosas de la portada. Sin este archivo todo sigue legible y con sus enlaces:
   1. Los fragmentos. Se barajan una vez por visita y se avanzan a mano, sin avance automático.
      El orden y el fragmento a la vista se guardan en la sesión, así el cambio de idioma conserva
      el mismo fragmento. Si algo falla, queda GB-ED01-F001, quieto.
   2. El panel de lectura. «Leer en contexto» y «Qué contamos» abren su ficha encima de la página,
      sin salir de ella. Se cierra con Esc, con su botón o tocando afuera, y el foco vuelve al
      enlace que lo abrió.
   3. Las esquinas del centro. Cada tráiler prueba su versión completa en el tamaño real de la
      pantalla y, si no cabe, guarda piezas enteras en un orden fijo, de lo accesorio a lo esencial.
      La letra no se achica: lo guardado sigue completo en su sala. */
(function () {
  'use strict';
  var d = document, w = window;
  var CLAVE = 'gb-ed01-fragmentos';

  function lista(sel, raiz) { return Array.prototype.slice.call((raiz || d).querySelectorAll(sel)); }

  /* ---------- 1. los fragmentos ---------- */
  var rotadores = lista('[data-rotador]');
  var visita = null;

  function barajar(ids) {
    var orden = ids.slice();
    for (var i = orden.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = orden[i]; orden[i] = orden[j]; orden[j] = t;
    }
    return orden;
  }
  function leerVisita(ids) {
    var v = null;
    try { v = JSON.parse(w.sessionStorage.getItem(CLAVE) || 'null'); } catch (e) { v = null; }
    var vale = v && Array.isArray(v.orden) && v.orden.length === ids.length &&
      ids.every(function (id) { return v.orden.indexOf(id) !== -1; });
    if (!vale) { var orden = barajar(ids); v = { orden: orden, actual: orden[0] }; }
    if (v.orden.indexOf(v.actual) === -1) v.actual = v.orden[0];
    return v;
  }
  function guardar() {
    try { w.sessionStorage.setItem(CLAVE, JSON.stringify(visita)); } catch (e) { /* sin sesión: el orden vive en esta página */ }
  }
  function mostrar() {
    var n = visita.orden.indexOf(visita.actual) + 1, total = visita.orden.length;
    rotadores.forEach(function (r) {
      var hay = false;
      lista('.rot-pila > [data-fragmento]', r).forEach(function (f) {
        if (f.getAttribute('data-fragmento') === visita.actual) { f.setAttribute('data-actual', ''); hay = true; }
        else f.removeAttribute('data-actual');
      });
      var vacio = r.querySelector('.rot-vacio');
      if (vacio) vacio.hidden = hay;
      var c = r.querySelector('.rot-cuenta [data-n]');
      if (c) c.textContent = String(n);
      var t = r.querySelector('.rot-cuenta [data-t]');
      if (t) t.textContent = String(total);
    });
  }

  if (rotadores.length) {
    var ids = lista('.rot-pila > [data-fragmento]', rotadores[0]).map(function (f) { return f.getAttribute('data-fragmento'); });
    if (ids.length) {
      visita = leerVisita(ids);
      guardar();
      rotadores.forEach(function (r) {
        lista('.rot-pila > [data-fragmento]', r).forEach(function (f) { f.hidden = false; });
        r.classList.add('rotador--vivo');
        lista('[data-rot-controles]', r).forEach(function (c) { c.hidden = false; });
      });
      mostrar();
      // la sala del laboratorio lee los otros fragmentos en el orden de esta visita
      var voces = d.querySelector('[data-voces]');
      if (voces) visita.orden.forEach(function (id) {
        var f = voces.querySelector('[data-fragmento="' + id + '"]');
        if (f) voces.appendChild(f);
      });
      d.addEventListener('click', function (e) {
        var b = e.target.closest ? e.target.closest('[data-rot]') : null;
        if (!b) return;
        var paso = parseInt(b.getAttribute('data-rot'), 10) || 0;
        var i = visita.orden.indexOf(visita.actual), total = visita.orden.length;
        visita.actual = visita.orden[(i + paso + total) % total];
        guardar();
        var r = b.closest('[data-rotador]');
        if (r) r.classList.add('rotador--tocado');
        mostrar();   // el foco se queda en el botón: nadie se pierde
      });
    }
  }

  /* ---------- 3. las esquinas del centro ---------- */
  // Cada lista va de la versión completa a la mínima. Lo que se guarda primero es lo accesorio.
  var ETAPAS = {
    'q--preguntas': [[], ['.q-gancho'], ['.q-gancho', '.tri-nota dd'], ['.q-gancho', '.triptico'],
      ['.q-gancho', '.triptico', '.q-rotulo']],
    // el laboratorio prefiere el fragmento a su invitación: el recuadro «Laboratorio» queda justo debajo
    'q--laboratorio': [[], ['.q-gancho'], ['.q-gancho', '.q-enlace'], ['.rotador'], ['.rotador', '.q-gancho'],
      ['.rotador', '.q-gancho', '.cifras-que'], ['.rotador', '.q-gancho', '.cifras']],
    'q--resultados': [[], ['.q-gancho'], ['.q-gancho', '.resumen-mini'], ['.q-gancho', '.resumen-mini', '.c-conf'],
      ['.q-gancho', '.resumen-mini', '.c-conf', '.ruta'], ['.q-gancho', '.resumen-mini', '.ruta', '.cohorte-mini'],
      ['.q-gancho', '.resumen-mini', '.ruta', '.cohorte-mini', '.q-rotulo']],
    'q--como-medimos': [[], ['.q-gancho'], ['.q-gancho', '.q-alcance'], ['.q-gancho', '.q-alcance', '.sello-q'],
      ['.q-gancho', '.q-alcance', '.sellos'], ['.q-gancho', '.q-alcance', '.sellos', '.q-rotulo']]
  };
  var esquinas = lista('.cuadrante');
  function cabe(c) {
    var r = c.getBoundingClientRect(), cs = w.getComputedStyle(c);
    var arriba = r.top + parseFloat(cs.paddingTop) - .5, abajo = r.bottom - parseFloat(cs.paddingBottom) + .5;
    for (var i = 0; i < c.children.length; i++) {
      var h = c.children[i];
      if (!h.getClientRects().length) continue;
      var b = h.getBoundingClientRect();
      if (b.top < arriba || b.bottom > abajo) return false;
    }
    return true;
  }
  var escritorio = w.matchMedia ? w.matchMedia('(min-width: 900px)') : { matches: true };
  function ajustar() {
    if (!escritorio.matches) return;   // en el celular las esquinas son baldosas: no hay nada que ajustar
    esquinas.forEach(function (c) {
      if (!c.getClientRects().length) return;
      var etapas = null;
      for (var k in ETAPAS) if (c.classList.contains(k)) etapas = ETAPAS[k];
      if (!etapas) return;
      for (var i = 0; i < etapas.length; i++) {
        lista('[data-guardado]', c).forEach(function (e) { e.removeAttribute('data-guardado'); });
        etapas[i].forEach(function (sel) { lista(sel, c).forEach(function (e) { e.setAttribute('data-guardado', ''); }); });
        if (cabe(c)) break;
      }
    });
  }
  if (esquinas.length) {
    d.documentElement.classList.add('ajusta');
    ajustar();
    if (d.fonts && d.fonts.ready) d.fonts.ready.then(ajustar);
    var pedido = false;
    w.addEventListener('resize', function () {
      if (pedido) return;
      pedido = true;
      w.requestAnimationFrame(function () { pedido = false; ajustar(); });
    });
  }

  /* ---------- 2. el panel de lectura ---------- */
  var dlg = d.getElementById('panel-lectura');
  if (!dlg || typeof dlg.showModal !== 'function') return;   // sin panel, los enlaces llevan a la ficha
  var titulo = dlg.querySelector('.pl-titulo');
  var cuerpo = dlg.querySelector('.pl-cuerpo');
  var error = dlg.querySelector('.pl-error');
  var tituloBase = titulo ? titulo.textContent : '';
  var abridor = null;

  lista('a[data-panel]').forEach(function (a) { a.setAttribute('aria-haspopup', 'dialog'); });

  function abrir(id, desde) {
    var ficha = d.getElementById(id);
    var contenido = ficha ? ficha.querySelector('.panel-contenido') : null;
    abridor = desde || null;
    cuerpo.textContent = '';
    if (contenido) {
      var copia = contenido.cloneNode(true);
      lista('[id]', copia).forEach(function (n) { n.removeAttribute('id'); });
      cuerpo.appendChild(copia);
      if (titulo) titulo.textContent = contenido.getAttribute('data-panel-titulo') || tituloBase;
      error.hidden = true;
    } else {
      if (titulo) titulo.textContent = tituloBase;
      error.hidden = false;
    }
    dlg.showModal();
    cuerpo.scrollTop = 0;
    // la cita se lee en su lugar: el panel abre con el pasaje marcado a la vista
    var marca = cuerpo.querySelector('mark');
    if (marca && marca.getBoundingClientRect().bottom > cuerpo.getBoundingClientRect().bottom - 24) {
      cuerpo.scrollTop += marca.getBoundingClientRect().top - cuerpo.getBoundingClientRect().top - cuerpo.clientHeight / 3;
    }
  }

  d.addEventListener('click', function (e) {
    var a = e.target.closest ? e.target.closest('a[data-panel]') : null;
    if (!a || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    e.preventDefault();
    abrir(a.getAttribute('data-panel'), a);
  });
  dlg.addEventListener('click', function (e) {
    if (e.target.closest && e.target.closest('[data-cerrar]')) { dlg.close(); return; }
    if (e.target !== dlg) return;
    // un clic en el fondo oscuro, fuera del panel, también lo cierra
    var r = dlg.getBoundingClientRect();
    if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) dlg.close();
  });
  dlg.addEventListener('close', function () {
    cuerpo.textContent = '';
    if (abridor && abridor.isConnected && abridor.focus) abridor.focus({ preventScroll: true });
    abridor = null;
  });

  // quien llega con la dirección de una ficha (#fuente-…) la encuentra abierta
  function abrirFicha() {
    var id = location.hash.slice(1);
    var el = id ? d.getElementById(id) : null;
    if (el && el.tagName === 'DETAILS') el.open = true;
  }
  abrirFicha();
  w.addEventListener('hashchange', abrirFicha);
})();
