/* ==========================================================================
   Terrenos Bragado — landing page behaviour
   Vanilla JS, no build step. Scoped to the public landing page only.
   Modules: i18n · navbar · hero media · reveal · plot finder · contact form
   ========================================================================== */
(function () {
  "use strict";

  document.documentElement.classList.remove("no-js");

  var reduceMotionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
  var prefersReducedMotion = function () {
    return reduceMotionQuery.matches;
  };

  var $ = function (sel, root) {
    return (root || document).querySelector(sel);
  };
  var $$ = function (sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  };

  /* ========================================================================
     1. i18n
     Dictionaries live in /static/i18n/<lang>.json and are applied client-side
     via data-i18n attributes. The markup ships with Spanish copy inline, so
     the page is fully readable even if these fetches never resolve.
     ====================================================================== */
  var I18N = (function () {
    var SUPPORTED = ["es", "en", "pt"];
    var FALLBACK = "es";
    var STORAGE_KEY = "terrenos.lang";

    var dict = {};
    var current = FALLBACK;
    var listeners = [];

    function detect() {
      // 1. An explicit choice made earlier in this browser wins.
      try {
        var saved = window.localStorage.getItem(STORAGE_KEY);
        if (saved && SUPPORTED.indexOf(saved) !== -1) return saved;
      } catch (err) {
        /* Private mode / storage disabled — fall through to browser prefs. */
      }
      // 2. Otherwise follow the browser's preference order.
      var prefs = navigator.languages && navigator.languages.length
        ? navigator.languages
        : [navigator.language || navigator.userLanguage || ""];
      for (var i = 0; i < prefs.length; i++) {
        var base = String(prefs[i]).toLowerCase().split("-")[0];
        if (SUPPORTED.indexOf(base) !== -1) return base;
      }
      // 3. Neither matched — Spanish.
      return FALLBACK;
    }

    function get(key) {
      var parts = key.split(".");
      var node = dict;
      for (var i = 0; i < parts.length; i++) {
        if (node == null || typeof node !== "object") return null;
        node = node[parts[i]];
      }
      return typeof node === "string" ? node : null;
    }

    function t(key, vars) {
      var value = get(key);
      if (value === null) return null;
      if (!vars) return value;
      return value.replace(/\{(\w+)\}/g, function (match, name) {
        return Object.prototype.hasOwnProperty.call(vars, name) ? vars[name] : match;
      });
    }

    function apply(root) {
      $$("[data-i18n]", root || document).forEach(function (el) {
        var value = t(el.getAttribute("data-i18n"));
        if (value !== null) el.textContent = value;
      });

      // data-i18n-attr="placeholder:contact.name_ph;aria-label:nav.menu"
      $$("[data-i18n-attr]", root || document).forEach(function (el) {
        el.getAttribute("data-i18n-attr").split(";").forEach(function (pair) {
          var bits = pair.split(":");
          if (bits.length !== 2) return;
          var attr = bits[0].trim();
          var value = t(bits[1].trim());
          if (value !== null) el.setAttribute(attr, value);
        });
      });

      // Interpolated strings that need runtime values.
      $$("[data-i18n-year]").forEach(function (el) {
        var value = t(el.getAttribute("data-i18n-year"), { year: new Date().getFullYear() });
        if (value !== null) el.textContent = value;
      });

      var title = t("meta.title");
      if (title) document.title = title;
      var desc = t("meta.description");
      var descTag = $('meta[name="description"]');
      if (desc && descTag) descTag.setAttribute("content", desc);
    }

    function notify() {
      listeners.forEach(function (fn) {
        try {
          fn(current);
        } catch (err) {
          if (window.console) console.error("[i18n] listener failed", err);
        }
      });
    }

    function load(lang, persist) {
      var url = document.body.getAttribute("data-i18n-base") + lang + ".json";
      return fetch(url, { credentials: "same-origin" })
        .then(function (res) {
          if (!res.ok) throw new Error("HTTP " + res.status);
          return res.json();
        })
        .then(function (data) {
          dict = data;
          current = lang;
          document.documentElement.lang = lang;
          if (persist) {
            try {
              window.localStorage.setItem(STORAGE_KEY, lang);
            } catch (err) {
              /* Non-fatal: the choice just won't survive a reload. */
            }
          }
          apply();
          notify();
        })
        .catch(function (err) {
          // Inline Spanish copy stays on screen; nothing is blanked out.
          if (window.console) console.warn("[i18n] could not load " + lang, err);
        });
    }

    return {
      supported: SUPPORTED,
      detect: detect,
      load: load,
      t: t,
      apply: apply,
      current: function () {
        return current;
      },
      onChange: function (fn) {
        listeners.push(fn);
      }
    };
  })();

  /* ---- Language switcher (nav + footer instances stay in sync) ---------- */
  function initLangSwitchers() {
    var switchers = $$(".lang");
    if (!switchers.length) return;

    function closeAll(except) {
      switchers.forEach(function (sw) {
        if (sw === except) return;
        $(".lang__toggle", sw).setAttribute("aria-expanded", "false");
        $(".lang__menu", sw).hidden = true;
      });
    }

    function syncLabels(lang) {
      switchers.forEach(function (sw) {
        $(".lang__code", sw).textContent = lang.toUpperCase();
        $$(".lang__option", sw).forEach(function (opt) {
          opt.setAttribute("aria-checked", String(opt.dataset.lang === lang));
        });
      });
    }

    switchers.forEach(function (sw) {
      var toggle = $(".lang__toggle", sw);
      var menu = $(".lang__menu", sw);

      toggle.addEventListener("click", function () {
        var open = toggle.getAttribute("aria-expanded") === "true";
        closeAll(sw);
        toggle.setAttribute("aria-expanded", String(!open));
        menu.hidden = open;
        if (!open) {
          var checked = $('.lang__option[aria-checked="true"]', menu) || $(".lang__option", menu);
          if (checked) checked.focus();
        }
      });

      menu.addEventListener("click", function (event) {
        var opt = event.target.closest(".lang__option");
        if (!opt) return;
        I18N.load(opt.dataset.lang, true);
        toggle.setAttribute("aria-expanded", "false");
        menu.hidden = true;
        toggle.focus();
      });

      menu.addEventListener("keydown", function (event) {
        if (event.key !== "Escape") return;
        toggle.setAttribute("aria-expanded", "false");
        menu.hidden = true;
        toggle.focus();
      });
    });

    document.addEventListener("click", function (event) {
      if (!event.target.closest(".lang")) closeAll(null);
    });

    I18N.onChange(syncLabels);
    syncLabels(I18N.current());
  }

  /* ========================================================================
     2. Navbar — scroll state, mobile menu, scroll spy
     ====================================================================== */
  function initNav() {
    var nav = $(".site-nav");
    var toggle = $(".nav-toggle");
    var menu = $("#mobile-menu");
    var scrim = $(".nav-scrim");
    if (!nav) return;

    /* Solid background once the hero is behind us, so nav labels keep
       contrast against light page content. */
    var onScroll = function () {
      nav.classList.toggle("is-scrolled", window.scrollY > window.innerHeight * 0.7);
    };
    var ticking = false;
    window.addEventListener(
      "scroll",
      function () {
        if (ticking) return;
        ticking = true;
        window.requestAnimationFrame(function () {
          onScroll();
          ticking = false;
        });
      },
      { passive: true }
    );
    onScroll();

    /* ---- Mobile menu ---- */
    function setMenu(open) {
      if (!toggle || !menu) return;
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute(
        "aria-label",
        I18N.t(open ? "nav.menu_close" : "nav.menu") || toggle.getAttribute("aria-label")
      );
      menu.hidden = !open;
      if (scrim) scrim.hidden = !open;
      // The menu panel is light; without this the transparent over-hero nav
      // would render white text on a white surface.
      nav.classList.toggle("is-solid", open);
      document.body.style.overflow = open ? "hidden" : "";
    }

    if (toggle && menu) {
      toggle.addEventListener("click", function () {
        setMenu(toggle.getAttribute("aria-expanded") !== "true");
      });

      menu.addEventListener("click", function (event) {
        if (event.target.closest("a")) setMenu(false);
      });

      if (scrim) scrim.addEventListener("click", function () { setMenu(false); });

      document.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") {
          setMenu(false);
          toggle.focus();
        }
      });

      // Leaving the mobile breakpoint must not strand the page in menu state.
      var mq = window.matchMedia("(min-width: 768px)");
      var onBreakpoint = function (e) {
        if (e.matches) setMenu(false);
      };
      if (mq.addEventListener) mq.addEventListener("change", onBreakpoint);
      else if (mq.addListener) mq.addListener(onBreakpoint);
    }

    /* ---- Scroll spy: mark the section currently in view ---- */
    var links = $$(".nav-link[data-section]");
    var sections = links
      .map(function (link) { return document.getElementById(link.dataset.section); })
      .filter(Boolean);

    if (sections.length && "IntersectionObserver" in window) {
      var spy = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (!entry.isIntersecting) return;
            links.forEach(function (link) {
              if (link.dataset.section === entry.target.id) {
                link.setAttribute("aria-current", "true");
              } else {
                link.removeAttribute("aria-current");
              }
            });
          });
        },
        { rootMargin: "-45% 0px -50% 0px", threshold: 0 }
      );
      sections.forEach(function (section) { spy.observe(section); });
    }
  }

  /* ========================================================================
     3. Hero media — cross-faded video rotation
     Muted/autoplay/loop with a poster fallback. Under prefers-reduced-motion
     the videos never start and the poster is the hero background.
     ====================================================================== */
  function initHeroMedia() {
    var media = $(".hero__media");
    if (!media) return;

    var control = $(".hero__mediactrl");
    var videos = $$(".hero__video", media);
    var index = 0;
    var timer = null;
    var userPaused = false;
    var ROTATE_MS = 9000;
    var available = [];

    function hideControl() {
      if (control) control.hidden = true;
    }

    if (!videos.length) {
      hideControl();
      return;
    }

    // Reduced motion: static poster only. Drop the video elements entirely so
    // nothing downloads or decodes in the background.
    if (prefersReducedMotion()) {
      videos.forEach(function (v) { v.remove(); });
      hideControl();
      return;
    }

    videos.forEach(function (video) {
      video.addEventListener(
        "loadeddata",
        function () {
          if (available.indexOf(video) === -1) available.push(video);
          if (available.length === 1) {
            // First playable file: reveal the control and start the loop.
            if (control) control.hidden = false;
            activate(video);
          } else {
            // A second file makes rotation possible — arm the interval.
            start();
          }
        },
        { once: true }
      );
      // Missing/unplayable source: stay on the poster rather than flash black.
      video.addEventListener("error", function () {
        video.classList.remove("is-active");
        var pos = available.indexOf(video);
        if (pos !== -1) available.splice(pos, 1);
        if (!available.length) {
          hideControl();
          stop();
        }
      });
    });

    function activate(video) {
      videos.forEach(function (v) { v.classList.toggle("is-active", v === video); });
      var play = video.play();
      if (play && typeof play.catch === "function") {
        // Autoplay can be refused (e.g. data saver); the poster remains.
        play.catch(function () {});
      }
    }

    function advance() {
      if (available.length < 2) return;
      index = (index + 1) % available.length;
      activate(available[index]);
    }

    // preload="none" means nothing is fetched until we ask, so neither
    // "loadeddata" nor "error" would ever fire on its own. Kick the fetch off
    // the first time the hero is actually on screen.
    var primed = false;
    function prime() {
      if (primed) return;
      primed = true;
      videos.forEach(function (video) {
        try {
          video.load();
        } catch (err) {
          /* Ignored: the error handler above takes it out of the rotation. */
        }
      });
    }

    function start() {
      if (userPaused || prefersReducedMotion()) return;
      prime();
      if (timer) return;
      if (available.length) activate(available[index % available.length]);
      if (available.length > 1) timer = window.setInterval(advance, ROTATE_MS);
    }

    function stop() {
      if (timer) {
        window.clearInterval(timer);
        timer = null;
      }
      videos.forEach(function (v) {
        if (!v.paused) v.pause();
      });
    }

    if (control) {
      control.addEventListener("click", function () {
        userPaused = !userPaused;
        control.setAttribute("aria-pressed", String(userPaused));
        control.setAttribute(
          "aria-label",
          I18N.t(userPaused ? "hero.play" : "hero.pause") || control.getAttribute("aria-label")
        );
        $(".icon-pause", control).hidden = userPaused;
        $(".icon-play", control).hidden = !userPaused;
        if (userPaused) stop();
        else start();
      });
    }

    // Pause when the hero scrolls out of view or the tab is hidden.
    if ("IntersectionObserver" in window) {
      var io = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) start();
            else stop();
          });
        },
        { threshold: 0.15 }
      );
      io.observe(media);
    } else {
      start();
    }

    document.addEventListener("visibilitychange", function () {
      if (document.hidden) stop();
      else start();
    });

    // Honour a mid-session change to the motion preference.
    var onMotionChange = function () {
      if (prefersReducedMotion()) {
        stop();
        videos.forEach(function (v) { v.classList.remove("is-active"); });
        hideControl();
      }
    };
    if (reduceMotionQuery.addEventListener) reduceMotionQuery.addEventListener("change", onMotionChange);
    else if (reduceMotionQuery.addListener) reduceMotionQuery.addListener(onMotionChange);
  }

  /* ========================================================================
     4. Scroll reveal — one subtle motion per section, staggered per card
     ====================================================================== */
  function initReveal() {
    var items = $$(".reveal");
    if (!items.length) return;

    if (prefersReducedMotion() || !("IntersectionObserver" in window)) {
      items.forEach(function (el) { el.classList.add("is-visible"); });
      return;
    }

    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("is-visible");
          io.unobserve(entry.target);
        });
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.08 }
    );

    items.forEach(function (el) { io.observe(el); });

    // 40ms stagger within each grid, capped so late cards don't lag.
    $$("[data-stagger]").forEach(function (group) {
      $$(".reveal", group).forEach(function (el, i) {
        el.style.setProperty("--reveal-delay", Math.min(i * 40, 320) + "ms");
      });
    });
  }

  /* ========================================================================
     5. Plot finder
     Filters are fully wired; the dataset below is a client-side mock so the
     UI can be reviewed before the backend search exists.
     ====================================================================== */

  // TODO: wire to backend search endpoint.
  // Replace MOCK_LOTS + filterLots() with a fetch to a Django view, e.g.
  //   GET /api/lands/search/?project=<id>&price_min=&price_max=&size=
  // returning JSON rows from lands.models.Land (filter status='available').
  // Keep the render/empty-state/aria-live plumbing below as-is.
  var MOCK_LOTS = [
    { id: "A-12", project: "p1", projectName: "Los Álamos", area: 480, dims: "16 × 30 m", price: 14200, status: "available" },
    { id: "A-27", project: "p1", projectName: "Los Álamos", area: 300, dims: "10 × 30 m", price: 12500, status: "available" },
    { id: "B-03", project: "p2", projectName: "Santa Rosa", area: 625, dims: "25 × 25 m", price: 19800, status: "available" },
    { id: "B-14", project: "p2", projectName: "Santa Rosa", area: 450, dims: "15 × 30 m", price: 15900, status: "reserved" },
    { id: "C-08", project: "p3", projectName: "El Mirador", area: 900, dims: "30 × 30 m", price: 28900, status: "available" },
    { id: "C-11", project: "p3", projectName: "El Mirador", area: 720, dims: "24 × 30 m", price: 22400, status: "available" },
    { id: "D-02", project: "p4", projectName: "Las Acacias", area: 288, dims: "12 × 24 m", price: 11200, status: "available" },
    { id: "D-19", project: "p4", projectName: "Las Acacias", area: 384, dims: "12 × 32 m", price: 13750, status: "available" },
    { id: "E-05", project: "p5", projectName: "Don Bosco", area: 550, dims: "22 × 25 m", price: 21000, status: "available" },
    { id: "E-09", project: "p5", projectName: "Don Bosco", area: 275, dims: "11 × 25 m", price: 16400, status: "reserved" },
    { id: "F-01", project: "p6", projectName: "La Estancia", area: 1250, dims: "25 × 50 m", price: 34500, status: "available" },
    { id: "F-07", project: "p6", projectName: "La Estancia", area: 1000, dims: "25 × 40 m", price: 26750, status: "available" }
  ];

  var SIZE_BUCKETS = {
    s1: [0, 300],
    s2: [300, 500],
    s3: [500, 800],
    s4: [800, Infinity]
  };

  function initFinder() {
    var form = $("#finder-form");
    if (!form) return;

    var list = $("#finder-results");
    var empty = $("#finder-empty");
    var count = $("#finder-count");
    var resetBtn = $("#finder-reset");
    var lastResults = MOCK_LOTS.slice();

    function filterLots() {
      var project = form.elements["project"].value;
      var min = parseFloat(form.elements["price_min"].value);
      var max = parseFloat(form.elements["price_max"].value);
      var size = form.elements["size"].value;
      var bucket = SIZE_BUCKETS[size];

      return MOCK_LOTS.filter(function (lot) {
        if (project && lot.project !== project) return false;
        if (!isNaN(min) && lot.price < min) return false;
        if (!isNaN(max) && lot.price > max) return false;
        if (bucket && (lot.area < bucket[0] || lot.area >= bucket[1])) return false;
        return true;
      });
    }

    function money(value) {
      try {
        return new Intl.NumberFormat(I18N.current() === "en" ? "en-US" : "es-AR", {
          style: "currency",
          currency: "USD",
          maximumFractionDigits: 0
        }).format(value);
      } catch (err) {
        return "USD " + value;
      }
    }

    function number(value) {
      try {
        return new Intl.NumberFormat(I18N.current() === "en" ? "en-US" : "es-AR").format(value);
      } catch (err) {
        return String(value);
      }
    }

    function render(results) {
      lastResults = results;
      list.textContent = "";

      var n = results.length;
      var key = n === 1 ? "finder.results_count_one" : "finder.results_count_other";
      count.textContent = I18N.t(key, { n: number(n) }) || n + " / " + MOCK_LOTS.length;

      empty.hidden = n > 0;
      list.hidden = n === 0;

      results.forEach(function (lot) {
        var li = document.createElement("li");
        li.className = "lot";

        var id = document.createElement("p");
        id.className = "lot__id";
        id.textContent = "Lote " + lot.id;

        var project = document.createElement("p");
        project.className = "lot__project";
        project.textContent = lot.projectName;

        var stats = document.createElement("div");
        stats.className = "lot__stats";

        var area = document.createElement("span");
        area.className = "chip";
        area.textContent = (I18N.t("finder.area", { n: number(lot.area) }) || lot.area + " m²");

        var dims = document.createElement("span");
        dims.className = "chip";
        dims.textContent = lot.dims;

        var status = document.createElement("span");
        status.className = "chip";
        status.textContent =
          I18N.t(lot.status === "available" ? "finder.status_available" : "finder.status_reserved") ||
          lot.status;

        stats.append(area, dims, status);

        var price = document.createElement("p");
        price.className = "lot__price";
        price.textContent = money(lot.price);

        li.append(id, project, stats, price);
        list.appendChild(li);
      });
    }

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      render(filterLots());
    });

    if (resetBtn) {
      resetBtn.addEventListener("click", function () {
        form.reset();
        render(MOCK_LOTS.slice());
      });
    }

    // Re-render so results follow a language change.
    I18N.onChange(function () { render(lastResults); });

    render(MOCK_LOTS.slice());
  }

  /* ========================================================================
     6. Contact form — client-side validation only (no submission yet)
     ====================================================================== */
  function initContactForm() {
    var form = $("#contact-form");
    if (!form) return;

    var summary = $("#contact-summary");
    var summaryList = $("#contact-summary-list");
    var status = $("#contact-status");
    // Deliberately permissive: overly strict email regexes reject valid addresses.
    var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

    var RULES = {
      name: function (value) { return value.trim().length >= 2; },
      email: function (value) { return EMAIL_RE.test(value.trim()); },
      message: function (value) { return value.trim().length >= 10; }
    };

    function fieldOf(input) {
      return input.closest(".form-field");
    }

    function setValid(input, valid) {
      var field = fieldOf(input);
      if (!field) return;
      field.classList.toggle("is-invalid", !valid);
      input.setAttribute("aria-invalid", String(!valid));
    }

    function validate(input) {
      var rule = RULES[input.name];
      if (!rule) return true;
      var valid = rule(input.value);
      setValid(input, valid);
      return valid;
    }

    var inputs = Object.keys(RULES).map(function (name) { return form.elements[name]; });

    inputs.forEach(function (input) {
      // Validate on blur, not on every keystroke.
      input.addEventListener("blur", function () { validate(input); });
      // Once a field is marked invalid, let the user see it recover as they type.
      input.addEventListener("input", function () {
        if (fieldOf(input).classList.contains("is-invalid")) validate(input);
      });
    });

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      status.hidden = true;

      var invalid = inputs.filter(function (input) { return !validate(input); });

      if (invalid.length) {
        // One bad field: focus it. Several: focus a linked summary instead.
        if (invalid.length === 1) {
          summary.hidden = true;
          invalid[0].focus();
          return;
        }

        summaryList.textContent = "";
        invalid.forEach(function (input) {
          var li = document.createElement("li");
          var link = document.createElement("a");
          link.href = "#" + input.id;
          link.textContent =
            I18N.t("contact." + (input.name === "message" ? "msg" : input.name) + "_err") ||
            $(".form-field__error", fieldOf(input)).textContent;
          link.addEventListener("click", function (e) {
            e.preventDefault();
            input.focus();
          });
          li.appendChild(link);
          summaryList.appendChild(li);
        });
        summary.hidden = false;
        summary.focus();
        return;
      }

      summary.hidden = true;

      // TODO: POST to a Django contact endpoint (with CSRF token) once it exists.
      // For now the form only demonstrates validation + success feedback.
      status.hidden = false;
      form.reset();
      inputs.forEach(function (input) {
        fieldOf(input).classList.remove("is-invalid");
        input.removeAttribute("aria-invalid");
      });
    });
  }

  /* ========================================================================
     Boot
     ====================================================================== */
  function boot() {
    initLangSwitchers();
    initNav();
    initHeroMedia();
    initReveal();
    initFinder();
    initContactForm();
    I18N.load(I18N.detect(), false);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
