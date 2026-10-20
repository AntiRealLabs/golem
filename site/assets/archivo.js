/* Golem Bench · el archivo
   Atiende cuatro cosas. Sin este archivo todo sigue legible y con sus enlaces:
   1. Los carruseles de pasajes. Cada colección se baraja una vez por visita y se avanza a mano, sin avance
      automático. El orden y el pasaje a la vista se guardan en la sesión, así el cambio de idioma conserva
      el mismo pasaje. Los de ED02-X1 traen sus 60 tarjetas de una plantilla; sin script queda quieto el primero.
   2. El panel de lectura. «Leer en contexto» abre encima de la página el pasaje en su texto y las lecturas
      que lo citan, traídos de la página de su recorrido; las fichas de la misma página («Qué contamos», la
      nota de incidencias) se abren igual. Se cierra con Esc, con su botón o tocando afuera, y el foco vuelve
      al enlace que lo abrió.
   3. Las esquinas del centro. Cada tráiler prueba su versión completa en el tamaño real de la pantalla y,
      si no cabe, guarda piezas enteras en un orden fijo, de lo accesorio a lo esencial. La letra no se
      achica: lo guardado sigue completo en su sala.
   4. Las páginas de los recorridos. El pasaje que se sigue (por su ancla) se ilumina entero, aunque esté
      partido en tramos, y la ruta marca la etapa que se está leyendo. */
(function () {
  'use strict';
  var d = document, w = window;
  var CLAVES = { ed01: 'gb-ed01-fragmentos', x1: 'gb-x1-pasajes' };

  function lista(sel, raiz) { return Array.prototype.slice.call((raiz || d).querySelectorAll(sel)); }
  function sinModificadores(e) { return e.button === 0 && !e.metaKey && !e.ctrlKey && !e.shiftKey && !e.altKey; }

  /* ---------- 1. los carruseles ---------- */
  var colecciones = {};
  lista('[data-rotador]').forEach(function (r) {
    var nombre = r.getAttribute('data-coleccion') || 'ed01';
    var plantilla = r.getAttribute('data-plantilla');
    if (plantilla) {
      var tpl = d.getElementById(plantilla), pila = r.querySelector('.rot-pila');
      if (!tpl || !tpl.content || !pila || !tpl.content.children.length) return;   // sin plantilla, queda el primero, quieto
      pila.textContent = '';
      pila.appendChild(tpl.content.cloneNode(true));
    }
    (colecciones[nombre] = colecciones[nombre] || { nombre: nombre, rotadores: [] }).rotadores.push(r);
  });

  function barajar(ids) {
    var orden = ids.slice();
    for (var i = orden.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = orden[i]; orden[i] = orden[j]; orden[j] = t;
    }
    return orden;
  }
  function leerVisita(clave, ids) {
    var v = null;
    try { v = JSON.parse(w.sessionStorage.getItem(clave) || 'null'); } catch (e) { v = null; }
    var vale = v && Array.isArray(v.orden) && v.orden.length === ids.length &&
      ids.every(function (id) { return v.orden.indexOf(id) !== -1; });
    if (!vale) { var orden = barajar(ids); v = { orden: orden, actual: orden[0] }; }
    if (v.orden.indexOf(v.actual) === -1) v.actual = v.orden[0];
    return v;
  }
  function guardar(c) {
    try { w.sessionStorage.setItem(c.clave, JSON.stringify(c.visita)); } catch (e) { /* sin sesión: el orden vive en esta página */ }
  }
  function mostrar(c) {
    var n = c.visita.orden.indexOf(c.visita.actual) + 1, total = c.visita.orden.length;
    c.rotadores.forEach(function (r) {
      var hay = false;
      lista('.rot-pila > [data-fragmento]', r).forEach(function (f) {
        if (f.getAttribute('data-fragmento') === c.visita.actual) { f.setAttribute('data-actual', ''); hay = true; }
        else f.removeAttribute('data-actual');
      });
      var vacio = r.querySelector('.rot-vacio');
      if (vacio) vacio.hidden = hay;
      var cn = r.querySelector('.rot-cuenta [data-n]');
      if (cn) cn.textContent = String(n);
      var ct = r.querySelector('.rot-cuenta [data-t]');
      if (ct) ct.textContent = String(total);
    });
  }
  Object.keys(colecciones).forEach(function (nombre) {
    var c = colecciones[nombre];
    var ids = lista('.rot-pila > [data-fragmento]', c.rotadores[0]).map(function (f) { return f.getAttribute('data-fragmento'); });
    if (!ids.length) return;
    c.clave = CLAVES[nombre] || ('gb-' + nombre);
    c.visita = leerVisita(c.clave, ids);
    guardar(c);
    c.rotadores.forEach(function (r) {
      lista('.rot-pila > [data-fragmento]', r).forEach(function (f) { f.hidden = false; });
      r.classList.add('rotador--vivo');
      lista('[data-rot-controles]', r).forEach(function (k) { k.hidden = false; });
    });
    mostrar(c);
    c.vivo = true;
  });
  d.addEventListener('click', function (e) {
    var b = e.target.closest ? e.target.closest('[data-rot]') : null;
    if (!b) return;
    var r = b.closest('[data-rotador]');
    var c = r ? colecciones[r.getAttribute('data-coleccion') || 'ed01'] : null;
    if (!c || !c.vivo) return;
    var paso = parseInt(b.getAttribute('data-rot'), 10) || 0;
    var i = c.visita.orden.indexOf(c.visita.actual), total = c.visita.orden.length;
    c.visita.actual = c.visita.orden[(i + paso + total) % total];
    guardar(c);
    r.classList.add('rotador--tocado');
    mostrar(c);   // el foco se queda en el botón: nadie se pierde
  });

  /* ---------- 3. las esquinas del centro ---------- */
  // Cada lista va de la versión completa a la mínima. Lo que se guarda primero es lo accesorio;
  // en resultados, la etiqueta del piloto y la cifra con su advertencia son lo último que se guarda.
  var ETAPAS = {
    'q--preguntas': [[], ['.q-rotulo'], ['.q-rotulo', '.pesa'], ['.q-rotulo', '.pesa', '.q-cuerpo']],
    'q--laboratorio': [[], ['.q-rotulo'], ['.q-rotulo', '.rotador'], ['.q-rotulo', '.rotador', '.q-cuerpo']],
    'q--resultados': [[], ['.q-rotulo'], ['.q-rotulo', '.x1-mini', '.x1-mini-ley'], ['.q-rotulo', '.x1-mini', '.x1-mini-ley', '.q-cuerpo']],
    'q--como-medimos': [[], ['.q-rotulo'], ['.q-rotulo', '.lee'], ['.q-rotulo', '.lee', '.q-cuerpo']]
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

  /* ---------- 4. las páginas de los recorridos ---------- */
  function iluminar(raiz, pid) {
    lista('.cita.activa', raiz).forEach(function (s) { s.classList.remove('activa'); });
    if (!pid || !/^p-(a|b|r1|r2|e)-\d+-\d+$/.test(pid)) return null;
    var tramos = lista('.cita[data-p~="' + pid + '"]', raiz);
    tramos.forEach(function (s) { s.classList.add('activa'); });
    return tramos[0] || null;
  }
  // quien llega con el ancla de algo guardado en un desplegable (una ficha, la lista de pasajes) lo encuentra abierto
  function abrirDestino() {
    var id = location.hash.slice(1);
    var el = id ? d.getElementById(id) : null;
    if (!el) return;
    if (el.tagName === 'DETAILS') el.open = true;
    for (var p = el.parentElement; p; p = p.parentElement) if (p.tagName === 'DETAILS') p.open = true;
    if (d.body.classList.contains('lectura-x1')) iluminar(d, id);
  }
  abrirDestino();
  w.addEventListener('hashchange', abrirDestino);

  var ruta = d.querySelector('.rc-ruta');
  if (ruta && 'IntersectionObserver' in w) {
    var enlaces = lista('a[href^="#"]', ruta);
    var visibles = {};
    var io = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (en) { visibles[en.target.id] = en.isIntersecting; });
      var actual = null;
      enlaces.forEach(function (a) { if (!actual && visibles[a.getAttribute('href').slice(1)]) actual = a; });
      enlaces.forEach(function (a) { if (a === actual) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current'); });
    }, { rootMargin: '-140px 0px -55% 0px' });
    enlaces.forEach(function (a) { var s = d.getElementById(a.getAttribute('href').slice(1)); if (s) io.observe(s); });
  }

  /* ---------- 2. el panel de lectura ---------- */
  var dlg = d.getElementById('panel-lectura');
  if (!dlg || typeof dlg.showModal !== 'function') return;   // sin panel, los enlaces llevan a la ficha o al recorrido
  var titulo = dlg.querySelector('.pl-titulo');
  var cuerpo = dlg.querySelector('.pl-cuerpo');
  var error = dlg.querySelector('.pl-error');
  var tituloBase = titulo ? titulo.textContent : '';
  var rotulos = d.getElementById('x1-panel-rotulos');
  var abridor = null;

  lista('a[data-panel]').forEach(function (a) { a.setAttribute('aria-haspopup', 'dialog'); });
  if (rotulos && w.fetch && w.DOMParser) lista('a[data-x1-pasaje]').forEach(function (a) { a.setAttribute('aria-haspopup', 'dialog'); });

  function sinIds(nodo) {
    if (nodo.removeAttribute) nodo.removeAttribute('id');
    lista('[id]', nodo).forEach(function (n) { n.removeAttribute('id'); });
    return nodo;
  }
  function el(tag, clase, txt) {
    var n = d.createElement(tag);
    if (clase) n.className = clase;
    if (txt != null) n.textContent = txt;
    return n;
  }

  function abrir(id, desde) {
    var ficha = d.getElementById(id);
    var contenido = ficha ? ficha.querySelector('.panel-contenido') : null;
    abridor = desde || null;
    cuerpo.textContent = '';
    if (contenido) {
      cuerpo.appendChild(sinIds(contenido.cloneNode(true)));
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

  // ED02-X1: el pasaje en su texto y las lecturas que lo citan, traídos de la página del recorrido
  var paginas = {};
  function cargar(url) {
    if (!paginas[url]) {
      paginas[url] = w.fetch(url, { credentials: 'same-origin' }).then(function (r) {
        if (!r.ok) throw new Error(String(r.status));
        return r.text();
      }).then(function (t) { return new w.DOMParser().parseFromString(t, 'text/html'); });
      paginas[url].catch(function () { delete paginas[url]; });
    }
    return paginas[url];
  }
  function abrirPasaje(href, desde) {
    var corte = href.indexOf('#'), url = href.slice(0, corte), pid = href.slice(corte + 1);
    var R = rotulos.dataset;
    abridor = desde || null;
    cuerpo.textContent = '';
    error.hidden = true;
    if (titulo) titulo.textContent = R.titulo;
    dlg.setAttribute('aria-busy', 'true');
    dlg.showModal();
    cargar(url).then(function (doc) {
      var ancla = doc.getElementById(pid);
      var texto = ancla ? ancla.closest('.rc-texto') : null;
      if (!texto) throw new Error('sin pasaje');
      var seccion = ancla.closest('.rc-rama') || ancla.closest('.rc-etapa');
      var etapa = ancla.closest('.rc-etapa').querySelector('.rc-etapa-t');
      var rama = ancla.closest('.rc-rama') ? ancla.closest('.rc-rama').querySelector('.rc-rama-t') : null;
      var meta = seccion ? seccion.querySelector('.rc-meta') : null;
      var cab = doc.querySelector('.rc-cabeza');
      var partes = [cab.querySelector('.eyebrow'), cab.querySelector('.rc-modelo'), cab.querySelector('.rc-caso-t'), etapa, rama]
        .filter(Boolean).map(function (n) { return n.textContent.trim(); });
      cuerpo.appendChild(el('p', 'px1-meta', partes.join(' · ')));
      if (meta) cuerpo.appendChild(sinIds(meta.cloneNode(true)));
      cuerpo.appendChild(el('p', 'px1-h', R.texto));
      var caja = el('div', 'px1-caja');
      var copia = sinIds(texto.cloneNode(true));
      caja.appendChild(copia);
      cuerpo.appendChild(caja);
      var primero = iluminar(copia, pid);
      cuerpo.appendChild(el('p', 'px1-h', R.jueces));
      var jueces = el('div', 'px1-jueces');
      var vistos = {};
      (ancla.getAttribute('data-cita') || '').split(/\s+/).forEach(function (par) {
        var jid = par.split(':')[0];
        if (!jid || vistos[jid]) return;
        vistos[jid] = true;
        var j = doc.getElementById(jid);
        if (j) jueces.appendChild(sinIds(j.cloneNode(true)));
      });
      cuerpo.appendChild(jueces);
      var ir = el('a', 'px1-abrir', R.abrir);
      ir.href = href;
      cuerpo.appendChild(ir);
      dlg.removeAttribute('aria-busy');
      cuerpo.scrollTop = 0;
      if (primero) caja.scrollTop = Math.max(0, primero.offsetTop - caja.offsetTop - caja.clientHeight / 3);
    }).catch(function () {
      dlg.removeAttribute('aria-busy');
      cuerpo.textContent = '';
      var p = el('p', 'pl-error', R.error + ' ');
      var a = el('a', null, href);
      a.href = href;
      p.appendChild(a);
      cuerpo.appendChild(p);
    });
  }

  d.addEventListener('click', function (e) {
    if (!e.target.closest || !sinModificadores(e)) return;
    var a = e.target.closest('a[data-panel]');
    if (a) { e.preventDefault(); abrir(a.getAttribute('data-panel'), a); return; }
    var x = e.target.closest('a[data-x1-pasaje]');
    if (x && rotulos && w.fetch && w.DOMParser) { e.preventDefault(); abrirPasaje(x.getAttribute('data-x1-pasaje'), x); }
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
})();
