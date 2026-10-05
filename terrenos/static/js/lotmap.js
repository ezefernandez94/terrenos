/* ==========================================================================
   Terrenos Bragado — interactive lot map (public project page)
   Vanilla JS, no dependencies. Loaded after landing.js, whose i18n module it
   reuses through window.TerrenosI18N.

   Data: GET <data-src> (projects.public_views.map_data) → { project, has_map, lots[] }
   SVG : already inlined and sanitized server-side; lot shapes carry
         data-shape-id (see docs/mapa-interactivo.md).
   ========================================================================== */
(function () {
  "use strict";

  var root = document.getElementById("lotmap");
  if (!root) return;

  var $ = function (sel, ctx) { return (ctx || document).querySelector(sel); };
  var $$ = function (sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); };
  var SVG_NS = "http://www.w3.org/2000/svg";

  var reduceMotionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
  var mobileQuery = window.matchMedia("(max-width: 767px)");

  /* ------------------------------------------------------------------------
     i18n — shared dictionary from landing.js, Spanish fallback for JS strings
     ---------------------------------------------------------------------- */
  var I18N = window.TerrenosI18N || {
    t: function () { return null; },
    current: function () { return "es"; },
    onChange: function () {}
  };

  var FALLBACK = {
    "lotmap.stat_total": "{n} lotes",
    "lotmap.stat_available": "{n} disponibles",
    "lotmap.stat_from": "Desde {price}",
    "lotmap.match_count_one": "{n} de {total} lotes coincide con tu búsqueda",
    "lotmap.match_count_other": "{n} de {total} lotes coinciden con tu búsqueda",
    "lotmap.map_label": "Plano de lotes. Usá Tab para recorrer los lotes y Enter para ver el detalle.",
    "lotmap.status_available": "Disponible",
    "lotmap.status_reserved": "Reservado",
    "lotmap.status_sold": "Vendido",
    "lotmap.status_unavailable": "No disponible",
    "lotmap.lot_title": "Lote {number}",
    "lotmap.block": "Manzana {block}",
    "lotmap.lot_aria": "Lote {number}, manzana {block}, {status}",
    "lotmap.area_value": "{n} m²",
    "lotmap.dims_value": "{width} × {length} m",
    "lotmap.price_on_request": "Consultar",
    "lotmap.reserved_note": "Este lote está reservado. Si la reserva se cae, vuelve a estar disponible en el plano.",
    "lotmap.sold_note": "Este lote ya fue vendido.",
    "lotmap.unavailable_note": "Este lote no está a la venta por el momento.",
    "lotmap.whatsapp_msg": "Hola! Me interesa el lote {number} de la manzana {block} en {project}. ¿Me podrían dar más información?",
    "lotmap.view_details": "Ver detalle",
    "lotmap.not_on_map": "Sin ubicación en el plano",
    "lotmap.page_title": "{project} — Plano de lotes | Terrenos Bragado",
    "lotmap.page_description": "Plano interactivo de lotes de {project}, Bragado: disponibilidad, medidas y precios."
  };

  function interpolate(text, vars) {
    if (!vars) return text;
    return text.replace(/\{(\w+)\}/g, function (match, name) {
      return Object.prototype.hasOwnProperty.call(vars, name) ? vars[name] : match;
    });
  }

  function t(key, vars) {
    var value = I18N.t(key, vars);
    if (value !== null && value !== undefined) return value;
    return interpolate(FALLBACK[key] || key, vars);
  }

  function locale() {
    return { en: "en-US", pt: "pt-BR" }[I18N.current()] || "es-AR";
  }

  function number(value, digits) {
    try {
      return new Intl.NumberFormat(locale(), { maximumFractionDigits: digits || 0 }).format(value);
    } catch (err) {
      return String(value);
    }
  }

  function money(value, currency) {
    try {
      return new Intl.NumberFormat(locale(), {
        style: "currency", currency: currency || "USD", maximumFractionDigits: 0
      }).format(value);
    } catch (err) {
      return (currency || "") + " " + number(value);
    }
  }

  function statusText(status) {
    return t("lotmap.status_" + status);
  }

  /* ------------------------------------------------------------------------
     State
     ---------------------------------------------------------------------- */
  var projectName = root.getAttribute("data-project") || "";
  var whatsapp = root.getAttribute("data-whatsapp") || "";
  var hasMap = root.getAttribute("data-has-map") === "1";

  var lots = [];
  var byShape = {};
  var selected = null;
  var lastTrigger = null;

  var form = $("#lotmap-filters");
  var countEl = $("#lotmap-count");
  var rowsEl = $("#lotmap-rows");
  var emptyEl = $(".lotmap__empty", root);
  var panel = $("#lotmap-panel");
  var errorEl = $(".lotmap__error", root);

  var SIZE_BUCKETS = { s1: [0, 300], s2: [300, 500], s3: [500, 800], s4: [800, Infinity] };

  /* ------------------------------------------------------------------------
     Map: SVG setup, painting, labels
     ---------------------------------------------------------------------- */
  var viewport = $(".lotmap__viewport", root);
  var svg = viewport ? $("svg", viewport) : null;
  var base = null;      // original viewBox {x, y, w, h}
  var vb = null;        // current viewBox
  var unit = 1;         // ~1/120 of the plan, used for patterns and label sizes
  var overlay = null;
  var labelsLayer = null;
  var MAX_ZOOM = 10;

  function parseViewBox(el) {
    var parts = (el.getAttribute("viewBox") || "").split(/[\s,]+/).map(parseFloat);
    if (parts.length !== 4 || parts.some(isNaN)) return null;
    return { x: parts[0], y: parts[1], w: parts[2], h: parts[3] };
  }

  function el(name, attrs, parent) {
    var node = document.createElementNS(SVG_NS, name);
    Object.keys(attrs || {}).forEach(function (k) { node.setAttribute(k, attrs[k]); });
    if (parent) parent.appendChild(node);
    return node;
  }

  function injectPatterns() {
    var defs = el("defs", {}, null);
    svg.insertBefore(defs, svg.firstChild);
    var s = unit * 1.6;

    // Sold: diagonal hatch — never colour alone
    var hatch = el("pattern", { id: "lotmap-hatch-sold", patternUnits: "userSpaceOnUse", width: s, height: s, patternTransform: "rotate(45)" }, defs);
    el("rect", { width: s, height: s, "class": "lotmap__pat-bg lotmap__pat-bg--sold" }, hatch);
    el("line", { x1: 0, y1: 0, x2: 0, y2: s, "class": "lotmap__pat-line lotmap__pat-line--sold", "stroke-width": s * 0.32 }, hatch);

    // Reserved: dots
    var dots = el("pattern", { id: "lotmap-dots-reserved", patternUnits: "userSpaceOnUse", width: s, height: s }, defs);
    el("rect", { width: s, height: s, "class": "lotmap__pat-bg lotmap__pat-bg--reserved" }, dots);
    el("circle", { cx: s / 2, cy: s / 2, r: s * 0.17, "class": "lotmap__pat-dot" }, dots);

    // Not available: cross-hatch
    var cross = el("pattern", { id: "lotmap-cross-unavailable", patternUnits: "userSpaceOnUse", width: s, height: s }, defs);
    el("rect", { width: s, height: s, "class": "lotmap__pat-bg lotmap__pat-bg--unavailable" }, cross);
    el("path", { d: "M0 0L" + s + " " + s + "M" + s + " 0L0 " + s, "class": "lotmap__pat-line lotmap__pat-line--unavailable", "stroke-width": s * 0.12 }, cross);
  }

  /* Bounding box of an element in root SVG user units (accounts for any group transforms). */
  function rootBBox(node) {
    var bb = node.getBBox();
    var rootCTM = svg.getScreenCTM();
    var nodeCTM = node.getScreenCTM();
    if (!rootCTM || !nodeCTM) return { x: bb.x, y: bb.y, w: bb.width, h: bb.height };
    var m = rootCTM.inverse().multiply(nodeCTM);
    var pts = [[bb.x, bb.y], [bb.x + bb.width, bb.y], [bb.x, bb.y + bb.height], [bb.x + bb.width, bb.y + bb.height]]
      .map(function (p) {
        var pt = svg.createSVGPoint();
        pt.x = p[0]; pt.y = p[1];
        return pt.matrixTransform(m);
      });
    var xs = pts.map(function (p) { return p.x; });
    var ys = pts.map(function (p) { return p.y; });
    var minX = Math.min.apply(null, xs), minY = Math.min.apply(null, ys);
    return { x: minX, y: minY, w: Math.max.apply(null, xs) - minX, h: Math.max.apply(null, ys) - minY };
  }

  function setupMap() {
    base = parseViewBox(svg);
    if (!base) return false;
    vb = { x: base.x, y: base.y, w: base.w, h: base.h };
    // Box follows the drawing's proportions; CSS caps it for very tall/wide plans
    viewport.style.aspectRatio = base.w + " / " + base.h;
    unit = Math.max(base.w, base.h) / 120;

    svg.classList.add("lotmap__svg");
    svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
    svg.setAttribute("role", "group");
    svg.setAttribute("aria-label", t("lotmap.map_label"));

    injectPatterns();
    overlay = el("g", { "class": "lotmap__overlay", "aria-hidden": "true" }, svg);
    labelsLayer = el("g", { "class": "lotmap__labels", "aria-hidden": "true" }, svg);

    $$("[data-shape-id]", svg).forEach(function (shape) {
      var lot = byShape[shape.getAttribute("data-shape-id")];
      if (!lot) {
        // Drawn but not linked to any land: shown neutral and inert
        shape.classList.add("lot-shape", "lot-shape--unlinked");
        return;
      }
      if (lot.el) return; // duplicate id in the drawing — first one wins
      lot.el = shape;
      shape.classList.add("lot-shape");
      shape.setAttribute("data-status", lot.status);
      shape.setAttribute("tabindex", "0");
      shape.setAttribute("role", "button");
      shape.addEventListener("keydown", function (event) {
        if (event.key === "Enter" || event.key === " " || event.key === "Spacebar") {
          event.preventDefault();
          select(lot, { source: "keyboard" });
        }
      });
      shape.addEventListener("focus", function () { ensureVisible(lot); });
      drawLabel(lot);
    });

    relabelMap();
    initPanZoom();
    return true;
  }

  function drawLabel(lot) {
    var box = rootBBox(lot.el);
    var cx = lot.label ? lot.label.x : box.x + box.w / 2;
    var cy = lot.label ? lot.label.y : box.y + box.h / 2;
    var size = Math.max(Math.min(box.w, box.h) * 0.3, unit * 0.5);
    size = Math.min(size, unit * 2.4);

    var text = el("text", {
      x: cx, y: cy, "class": "lotmap__label", "data-status": lot.status,
      "text-anchor": "middle", "dominant-baseline": "central", "font-size": size
    }, labelsLayer);
    var num = el("tspan", { x: cx }, text);
    num.textContent = lot.number;

    if (lot.status === "sold") {
      // Two lines: number above, "Vendido" below
      num.setAttribute("dy", -size * 0.35);
      lot.soldTag = el("tspan", { x: cx, dy: size * 0.95, "font-size": size * 0.5, "class": "lotmap__label-tag" }, text);
    }
    lot.labelEl = text;
    lot.box = box;
  }

  function relabelMap() {
    if (!svg) return;
    svg.setAttribute("aria-label", t("lotmap.map_label"));
    lots.forEach(function (lot) {
      if (lot.el) {
        lot.el.setAttribute("aria-label", t("lotmap.lot_aria", {
          number: lot.number, block: lot.block, status: statusText(lot.status)
        }));
      }
      if (lot.soldTag) lot.soldTag.textContent = statusText("sold");
    });
  }

  /* ------------------------------------------------------------------------
     Pan & zoom (viewBox based): drag, wheel, pinch, buttons, keyboard
     ---------------------------------------------------------------------- */
  function clampViewBox(v) {
    var w = Math.min(Math.max(v.w, base.w / MAX_ZOOM), base.w);
    var h = w * (base.h / base.w);
    // Keep the view centre inside the plan
    var cx = Math.min(Math.max(v.x + v.w / 2, base.x), base.x + base.w);
    var cy = Math.min(Math.max(v.y + v.h / 2, base.y), base.y + base.h);
    return { x: cx - w / 2, y: cy - h / 2, w: w, h: h };
  }

  function applyViewBox(v) {
    vb = clampViewBox(v);
    svg.setAttribute("viewBox", vb.x + " " + vb.y + " " + vb.w + " " + vb.h);
    root.classList.toggle("is-zoomed", vb.w < base.w * 0.999);
  }

  var animation = null;
  function animateTo(target) {
    target = clampViewBox(target);
    if (animation) window.cancelAnimationFrame(animation);
    if (reduceMotionQuery.matches) {
      applyViewBox(target);
      return;
    }
    var from = { x: vb.x, y: vb.y, w: vb.w, h: vb.h };
    var start = null;
    var DURATION = 280;
    function step(ts) {
      if (start === null) start = ts;
      var p = Math.min((ts - start) / DURATION, 1);
      var e = 1 - Math.pow(1 - p, 3);
      applyViewBox({
        x: from.x + (target.x - from.x) * e,
        y: from.y + (target.y - from.y) * e,
        w: from.w + (target.w - from.w) * e,
        h: from.h + (target.h - from.h) * e
      });
      animation = p < 1 ? window.requestAnimationFrame(step) : null;
    }
    animation = window.requestAnimationFrame(step);
  }

  function zoomAround(v, factor, point) {
    return {
      x: point.x - (point.x - v.x) * factor,
      y: point.y - (point.y - v.y) * factor,
      w: v.w * factor,
      h: v.h * factor
    };
  }

  function clientToSvg(clientX, clientY, inverse) {
    var pt = svg.createSVGPoint();
    pt.x = clientX; pt.y = clientY;
    return pt.matrixTransform(inverse || svg.getScreenCTM().inverse());
  }

  function center() {
    return { x: vb.x + vb.w / 2, y: vb.y + vb.h / 2 };
  }

  function zoomBy(factor) {
    animateTo(zoomAround(vb, factor, center()));
  }

  function resetView() {
    animateTo(base);
  }

  /* Pan (keeping zoom) so a focused lot is not off-screen. */
  function ensureVisible(lot) {
    var b = lot.box;
    if (!b) return;
    var inside = b.x >= vb.x && b.y >= vb.y && b.x + b.w <= vb.x + vb.w && b.y + b.h <= vb.y + vb.h;
    if (!inside) {
      applyViewBox({ x: b.x + b.w / 2 - vb.w / 2, y: b.y + b.h / 2 - vb.h / 2, w: vb.w, h: vb.h });
    }
  }

  /* Small screens: frame the selected lot above the bottom sheet. */
  function zoomToLot(lot) {
    var b = lot.box;
    if (!b) return;
    // ~3x the lot, but always at least 1.8x zoom so small screens get a closer look
    var w = Math.min(Math.max(b.w, b.h * (base.w / base.h)) * 3, base.w / 1.8);
    var h = w * (base.h / base.w);
    animateTo({ x: b.x + b.w / 2 - w / 2, y: b.y + b.h / 2 - h * 0.3, w: w, h: h });
  }

  function initPanZoom() {
    var pointers = {};
    var gesture = null;
    var DRAG_THRESHOLD = 6;

    function pointerList() {
      return Object.keys(pointers).map(function (k) { return pointers[k]; });
    }

    function startGesture() {
      var list = pointerList();
      var inverse = svg.getScreenCTM().inverse();
      gesture = { vb: { x: vb.x, y: vb.y, w: vb.w, h: vb.h }, inverse: inverse, moved: gesture ? gesture.moved : false };
      if (list.length === 1) {
        gesture.start = list[0];
      } else if (list.length >= 2) {
        var a = list[0], b = list[1];
        gesture.dist = Math.hypot(a.x - b.x, a.y - b.y) || 1;
        gesture.mid = { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 };
      }
    }

    viewport.addEventListener("pointerdown", function (event) {
      if (event.pointerType === "mouse" && event.button !== 0) return;
      pointers[event.pointerId] = { x: event.clientX, y: event.clientY, down: { x: event.clientX, y: event.clientY } };
      if (Object.keys(pointers).length === 1) {
        var shape = event.target.closest ? event.target.closest(".lot-shape:not(.lot-shape--unlinked)") : null;
        gesture = null;
        startGesture();
        gesture.target = shape;
      } else {
        // Second finger: switch to pinch; a pinch never counts as a tap
        startGesture();
        gesture.target = null;
        gesture.moved = true;
      }
      try { viewport.setPointerCapture(event.pointerId); } catch (err) { /* old browsers */ }
    });

    viewport.addEventListener("pointermove", function (event) {
      var p = pointers[event.pointerId];
      if (!p || !gesture) return;
      p.x = event.clientX; p.y = event.clientY;
      var list = pointerList();

      if (list.length === 1) {
        if (!gesture.moved && Math.hypot(p.x - p.down.x, p.y - p.down.y) < DRAG_THRESHOLD) return;
        gesture.moved = true;
        root.classList.add("is-dragging");
        var from = clientToSvg(gesture.start.down.x, gesture.start.down.y, gesture.inverse);
        var to = clientToSvg(p.x, p.y, gesture.inverse);
        applyViewBox({ x: gesture.vb.x + (from.x - to.x), y: gesture.vb.y + (from.y - to.y), w: gesture.vb.w, h: gesture.vb.h });
      } else if (list.length >= 2 && gesture.dist) {
        var a = list[0], b = list[1];
        var dist = Math.hypot(a.x - b.x, a.y - b.y) || 1;
        var mid = { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 };
        var startMid = clientToSvg(gesture.mid.x, gesture.mid.y, gesture.inverse);
        var nowMid = clientToSvg(mid.x, mid.y, gesture.inverse);
        var zoomed = zoomAround(gesture.vb, gesture.dist / dist, startMid);
        var scale = zoomed.w / gesture.vb.w;
        applyViewBox({
          x: zoomed.x - (nowMid.x - startMid.x) * scale,
          y: zoomed.y - (nowMid.y - startMid.y) * scale,
          w: zoomed.w, h: zoomed.h
        });
      }
    });

    function endPointer(event) {
      if (!pointers[event.pointerId]) return;
      delete pointers[event.pointerId];
      var remaining = Object.keys(pointers).length;
      if (remaining === 0) {
        root.classList.remove("is-dragging");
        if (event.type === "pointerup" && gesture && !gesture.moved && gesture.target) {
          var lot = byShape[gesture.target.getAttribute("data-shape-id")];
          if (lot) select(lot, { source: "pointer" });
        }
        gesture = null;
      } else {
        // One finger lifted from a pinch: continue as a drag from here
        var moved = gesture ? gesture.moved : true;
        startGesture();
        gesture.moved = moved;
        pointerList().forEach(function (p) { p.down = { x: p.x, y: p.y }; });
        gesture.start = pointerList()[0];
      }
    }
    viewport.addEventListener("pointerup", endPointer);
    viewport.addEventListener("pointercancel", endPointer);

    viewport.addEventListener("wheel", function (event) {
      event.preventDefault();
      var delta = event.deltaY * (event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? 400 : 1);
      var factor = Math.pow(1.0015, Math.max(Math.min(delta, 300), -300));
      if (animation) { window.cancelAnimationFrame(animation); animation = null; }
      applyViewBox(zoomAround(vb, factor, clientToSvg(event.clientX, event.clientY)));
    }, { passive: false });

    // Keyboard zoom while focus is anywhere inside the map
    viewport.addEventListener("keydown", function (event) {
      if (event.key === "+" || event.key === "=") { event.preventDefault(); zoomBy(1 / 1.5); }
      else if (event.key === "-" || event.key === "_") { event.preventDefault(); zoomBy(1.5); }
      else if (event.key === "0") { event.preventDefault(); resetView(); }
    });

    $$("[data-zoom]", root).forEach(function (btn) {
      btn.addEventListener("click", function () {
        var action = btn.getAttribute("data-zoom");
        if (action === "in") zoomBy(1 / 1.5);
        else if (action === "out") zoomBy(1.5);
        else resetView();
      });
    });
  }

  /* ------------------------------------------------------------------------
     Selection + detail panel (desktop side panel, mobile bottom sheet)
     ---------------------------------------------------------------------- */
  function updateOverlay() {
    if (!overlay) return;
    while (overlay.firstChild) overlay.removeChild(overlay.firstChild);
    lots.forEach(function (lot) { if (lot.el) lot.el.classList.remove("is-selected"); });
    if (!selected || !selected.el) return;

    selected.el.classList.add("is-selected");
    // Raised copy of the selected shape drawn above its neighbours. A real clone (not
    // <use>) so the page CSS still paints it by status.
    var copy = selected.el.cloneNode(true);
    ["id", "tabindex", "role", "aria-label"].forEach(function (a) { copy.removeAttribute(a); });
    copy.classList.add("lotmap__selected");
    var parentCTM = selected.el.parentNode.getScreenCTM && selected.el.parentNode.getScreenCTM();
    var rootCTM = svg.getScreenCTM();
    var wrap = el("g", {}, overlay);
    if (parentCTM && rootCTM) {
      var m = rootCTM.inverse().multiply(parentCTM);
      wrap.setAttribute("transform", "matrix(" + [m.a, m.b, m.c, m.d, m.e, m.f].join(" ") + ")");
    }
    wrap.appendChild(copy);
  }

  function renderPanel() {
    var body = $(".lotmap__panel-body", panel);
    var empty = $(".lotmap__panel-empty", panel);
    if (!selected) {
      body.hidden = true;
      empty.hidden = false;
      panel.setAttribute("data-open", "false");
      return;
    }
    var lot = selected;
    body.hidden = false;
    empty.hidden = true;
    panel.setAttribute("data-open", "true");

    $(".lotmap__panel-title", panel).textContent = t("lotmap.lot_title", { number: lot.number });
    $(".lotmap__panel-sub", panel).textContent = t("lotmap.block", { block: lot.block }) + " · " + projectName;

    var badge = $(".lotmap__badge", panel);
    badge.textContent = statusText(lot.status);
    badge.setAttribute("data-status", lot.status);

    $('[data-fact="area"]', panel).textContent = t("lotmap.area_value", { n: number(lot.area, 2) });
    $('[data-fact="dims"]', panel).textContent = t("lotmap.dims_value", { width: number(lot.width, 2), length: number(lot.length, 2) });

    var priced = lot.status === "available" || lot.status === "reserved";
    $('[data-fact-row="price"]', panel).hidden = !priced;
    $('[data-fact="price"]', panel).textContent = lot.price !== null ? money(lot.price, lot.currency) : t("lotmap.price_on_request");

    var note = $(".lotmap__note", panel);
    var noteKey = { reserved: "lotmap.reserved_note", sold: "lotmap.sold_note", unavailable: "lotmap.unavailable_note" }[lot.status];
    note.hidden = !noteKey;
    note.textContent = noteKey ? t(noteKey) : "";

    var cta = $(".lotmap__cta", panel);
    cta.hidden = !(lot.status === "available" && whatsapp);
    if (!cta.hidden) {
      var msg = t("lotmap.whatsapp_msg", { number: lot.number, block: lot.block, project: projectName });
      $("a", cta).href = "https://wa.me/" + whatsapp + "?text=" + encodeURIComponent(msg);
    }
  }

  function select(lot, opts) {
    opts = opts || {};
    selected = lot;
    lastTrigger = opts.trigger || lot.el || null;
    updateOverlay();
    renderPanel();
    rememberLot(lot);
    if (lot.el && mobileQuery.matches && currentView() === "map") zoomToLot(lot);
    if (opts.source === "keyboard" || opts.source === "list") {
      $(".lotmap__panel-title", panel).focus({ preventScroll: !mobileQuery.matches });
    }
  }

  function closePanel() {
    if (!selected) return;
    selected = null;
    updateOverlay();
    renderPanel();
    rememberLot(null);
    if (lastTrigger && document.body.contains(lastTrigger) && lastTrigger.getClientRects().length) {
      lastTrigger.focus({ preventScroll: true });
    }
    lastTrigger = null;
  }

  function rememberLot(lot) {
    if (!window.history.replaceState || !window.URLSearchParams) return;
    var params = new URLSearchParams(window.location.search);
    if (lot && lot.shape_id) params.set("lote", lot.shape_id);
    else params.delete("lote");
    var qs = params.toString();
    window.history.replaceState(null, "", window.location.pathname + (qs ? "?" + qs : "") + window.location.hash);
  }

  /* ------------------------------------------------------------------------
     Filters + list view
     ---------------------------------------------------------------------- */
  function readFilters() {
    if (!form) return {};
    return {
      min: parseFloat(form.elements["price_min"].value),
      max: parseFloat(form.elements["price_max"].value),
      bucket: SIZE_BUCKETS[form.elements["size"].value],
      availableOnly: form.elements["available"].checked
    };
  }

  function matches(lot, f) {
    if (f.availableOnly && lot.status !== "available") return false;
    if ((!isNaN(f.min) || !isNaN(f.max)) && lot.price === null) return false;
    if (!isNaN(f.min) && lot.price < f.min) return false;
    if (!isNaN(f.max) && lot.price > f.max) return false;
    if (f.bucket && (lot.area < f.bucket[0] || lot.area >= f.bucket[1])) return false;
    return true;
  }

  function applyFilters() {
    var f = readFilters();
    var n = 0;
    lots.forEach(function (lot) {
      lot.match = matches(lot, f);
      if (lot.match) n++;
      if (lot.el) lot.el.classList.toggle("is-dimmed", !lot.match);
      if (lot.labelEl) lot.labelEl.classList.toggle("is-dimmed", !lot.match);
    });
    if (countEl) {
      countEl.textContent = t(n === 1 ? "lotmap.match_count_one" : "lotmap.match_count_other", {
        n: number(n), total: number(lots.length)
      });
    }
    renderList();
  }

  function chip(text, extraClass) {
    var span = document.createElement("span");
    span.className = "chip" + (extraClass ? " " + extraClass : "");
    span.textContent = text;
    return span;
  }

  function renderList() {
    if (!rowsEl) return;
    rowsEl.textContent = "";
    var visible = lots.filter(function (lot) { return lot.match; });
    emptyEl.hidden = visible.length > 0;

    visible.forEach(function (lot) {
      var li = document.createElement("li");
      li.className = "lotrow";
      li.setAttribute("data-status", lot.status);

      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "lotrow__btn";
      btn.setAttribute("aria-label", t("lotmap.lot_aria", { number: lot.number, block: lot.block, status: statusText(lot.status) }) + ". " + t("lotmap.view_details"));

      var title = document.createElement("span");
      title.className = "lotrow__title";
      title.textContent = t("lotmap.lot_title", { number: lot.number }) + " · " + t("lotmap.block", { block: lot.block });

      var stats = document.createElement("span");
      stats.className = "lotrow__stats";
      var badge = chip(statusText(lot.status), "lotmap__badge");
      badge.setAttribute("data-status", lot.status);
      stats.append(
        badge,
        chip(t("lotmap.area_value", { n: number(lot.area, 2) })),
        chip(t("lotmap.dims_value", { width: number(lot.width, 2), length: number(lot.length, 2) }))
      );
      if (hasMap && !lot.el) stats.append(chip(t("lotmap.not_on_map")));

      var price = document.createElement("span");
      price.className = "lotrow__price";
      if (lot.status === "available" || lot.status === "reserved") {
        price.textContent = lot.price !== null ? money(lot.price, lot.currency) : t("lotmap.price_on_request");
      }

      btn.append(title, stats, price);
      btn.addEventListener("click", function () { select(lot, { source: "list", trigger: btn }); });
      li.appendChild(btn);
      rowsEl.appendChild(li);
    });
  }

  function currentView() {
    var pressed = $('.lotmap__view[aria-pressed="true"]', root);
    return pressed ? pressed.getAttribute("data-view") : "list";
  }

  function setView(view) {
    $$(".lotmap__view", root).forEach(function (btn) {
      btn.setAttribute("aria-pressed", String(btn.getAttribute("data-view") === view));
    });
    $$("[data-panel]", root).forEach(function (p) {
      p.hidden = p.getAttribute("data-panel") !== view;
    });
    root.setAttribute("data-view", view);
  }

  function initFilters() {
    if (!form) return;
    form.addEventListener("submit", function (event) { event.preventDefault(); });
    form.addEventListener("input", applyFilters);
    form.addEventListener("change", applyFilters);
    form.addEventListener("reset", function () { window.setTimeout(applyFilters, 0); });

    // Deep links: ?price_min=&price_max=&size=s2&available=1
    if (window.URLSearchParams) {
      var params = new URLSearchParams(window.location.search);
      ["price_min", "price_max", "size"].forEach(function (name) {
        if (params.get(name)) form.elements[name].value = params.get(name);
      });
      if (params.get("available") === "1") form.elements["available"].checked = true;
    }
  }

  /* ------------------------------------------------------------------------
     Static text that needs runtime values (stats chips in the header)
     ---------------------------------------------------------------------- */
  function relabelStatic() {
    // landing.js applies the landing's own meta.title/description on every language load
    document.title = t("lotmap.page_title", { project: projectName });
    var desc = $('meta[name="description"]');
    if (desc) desc.setAttribute("content", t("lotmap.page_description", { project: projectName }));

    $$("[data-lotmap-i18n]").forEach(function (node) {
      node.textContent = t(node.getAttribute("data-lotmap-i18n"), { n: number(parseFloat(node.getAttribute("data-n"))) });
    });
    $$("[data-lotmap-from]").forEach(function (node) {
      node.textContent = t("lotmap.stat_from", {
        price: money(parseFloat(node.getAttribute("data-lotmap-from")), node.getAttribute("data-currency"))
      });
    });
  }

  /* ------------------------------------------------------------------------
     Boot
     ---------------------------------------------------------------------- */
  function boot(data) {
    lots = data.lots || [];
    lots.forEach(function (lot) {
      lot.match = true;
      if (lot.shape_id) byShape[lot.shape_id] = lot;
    });

    var mapReady = hasMap && svg && setupMap();
    if (!mapReady) {
      hasMap = false;
      $$(".lotmap__views, [data-panel='map']", root).forEach(function (n) { n.hidden = true; });
      setView("list");
    } else {
      setView("map");
    }

    var legendUnavailable = $(".lotmap__legend-unavailable", root);
    if (legendUnavailable) {
      legendUnavailable.hidden = !lots.some(function (lot) { return lot.status === "unavailable"; });
    }

    $$(".lotmap__view", root).forEach(function (btn) {
      btn.addEventListener("click", function () { setView(btn.getAttribute("data-view")); });
    });
    $(".lotmap__close", panel).addEventListener("click", closePanel);
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && selected) closePanel();
    });

    initFilters();
    applyFilters();
    relabelStatic();

    if (window.URLSearchParams) {
      var wanted = new URLSearchParams(window.location.search).get("lote");
      if (wanted && byShape[wanted]) select(byShape[wanted], { source: "link" });
    }

    booted = true;
  }

  var booted = false;
  function onLanguage() {
    relabelStatic();
    if (!booted) return;
    relabelMap();
    applyFilters();
    renderPanel();
  }

  function start() {
    I18N.onChange(onLanguage);
    relabelStatic();
    fetch(root.getAttribute("data-src"), { credentials: "same-origin", headers: { Accept: "application/json" } })
      .then(function (res) {
        if (!res.ok) throw new Error("HTTP " + res.status);
        return res.json();
      })
      .then(boot)
      .catch(function (err) {
        if (window.console) console.error("[lotmap] could not load lots", err);
        if (errorEl) errorEl.hidden = false;
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
