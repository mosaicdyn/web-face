(function () {
  "use strict";

  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- Mobile menu ---------- */
  var burger = document.querySelector(".burger");
  var nav = document.getElementById("site-nav");
  if (burger && nav) {
    burger.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      burger.setAttribute("aria-expanded", open ? "true" : "false");
      burger.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    });
    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) {
        nav.classList.remove("is-open");
        burger.setAttribute("aria-expanded", "false");
      }
    });
  }

  /* ---------- Reveal on scroll ---------- */
  var io = "IntersectionObserver" in window ? IntersectionObserver : null;
  var reveals = document.querySelectorAll(".reveal");
  if (io && !reduceMotion) {
    var revealObs = new io(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("is-visible"); revealObs.unobserve(en.target); }
      });
    }, { threshold: 0.15 });
    reveals.forEach(function (el) { revealObs.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("is-visible"); });
  }

  /* ---------- "Fill text on scroll" heading ---------- */
  document.querySelectorAll(".fill-text__line").forEach(function (line) {
    var words = line.textContent.trim().split(/\s+/);
    line.textContent = "";
    words.forEach(function (w, i) {
      var s = document.createElement("span");
      s.className = "w";
      s.textContent = w;
      line.appendChild(s);
      if (i < words.length - 1) line.appendChild(document.createTextNode(" "));
    });
  });
  var fillWords = Array.prototype.slice.call(document.querySelectorAll(".fill-text .w"));
  function updateFill() {
    if (!fillWords.length) return;
    var el = fillWords[0].closest(".fill-text");
    var r = el.getBoundingClientRect();
    var vh = window.innerHeight;
    // 0 when the heading enters at the bottom, 1 when it reaches ~35% from the top
    var progress = (vh - r.top) / (vh * 0.65);
    progress = Math.max(0, Math.min(1, progress));
    var lit = Math.round(progress * fillWords.length);
    fillWords.forEach(function (w, i) { w.classList.toggle("is-lit", i < lit); });
  }
  if (reduceMotion) {
    fillWords.forEach(function (w) { w.classList.add("is-lit"); });
  } else {
    var ticking = false;
    window.addEventListener("scroll", function () {
      if (!ticking) { ticking = true; requestAnimationFrame(function () { updateFill(); ticking = false; }); }
    }, { passive: true });
    window.addEventListener("resize", updateFill);
    updateFill();
  }

  /* ---------- Marquees: duplicate items for a seamless loop ---------- */
  document.querySelectorAll(".marquee__track").forEach(function (track) {
    var items = Array.prototype.slice.call(track.children);
    items.forEach(function (item) {
      var c = item.cloneNode(true);
      c.setAttribute("aria-hidden", "true");
      track.appendChild(c);
    });
  });

  /* ---------- Count-up numbers ---------- */
  var counters = document.querySelectorAll(".count");
  function runCount(el) {
    var to = parseInt(el.getAttribute("data-to"), 10) || 0;
    if (reduceMotion) { el.textContent = "+" + to; return; }
    var start = null, dur = 1400;
    function step(ts) {
      if (!start) start = ts;
      var p = Math.min(1, (ts - start) / dur);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = "+" + Math.round(to * eased);
      if (p < 1) requestAnimationFrame(step);
    }
    el.textContent = "+0";
    requestAnimationFrame(step);
  }
  if (io) {
    var countObs = new io(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { runCount(en.target); countObs.unobserve(en.target); }
      });
    }, { threshold: 0.6 });
    counters.forEach(function (c) { countObs.observe(c); });
  }

  /* ---------- Footer: lamp switches on ---------- */
  var scene = document.getElementById("footer-scene");
  if (scene) {
    if (io && !reduceMotion) {
      var lampObs = new io(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) { scene.classList.add("is-lit"); lampObs.disconnect(); }
        });
      }, { threshold: 0.35 });
      lampObs.observe(scene);
    } else {
      scene.classList.add("is-lit");
    }
  }

  /* ---------- Contact form (Formspree) ---------- */
  var form = document.getElementById("contact-form");
  if (form) {
    var submit = form.querySelector(".form__submit");
    var status = form.querySelector(".form__status");
    var required = form.querySelectorAll("[required]");
    function validate() {
      var ok = true;
      required.forEach(function (f) { if (!f.value.trim() || !f.checkValidity()) ok = false; });
      submit.disabled = !ok;
      return ok;
    }
    form.addEventListener("input", validate);
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!validate()) return;
      submit.disabled = true;
      status.className = "form__status";
      status.textContent = "Sending…";
      fetch(form.action, { method: "POST", body: new FormData(form), headers: { Accept: "application/json" } })
        .then(function (res) {
          if (!res.ok) throw new Error("bad status");
          form.reset();
          status.className = "form__status is-ok";
          status.textContent = "Request sent! We’ll get back to you soon.";
        })
        .catch(function () {
          status.className = "form__status is-error";
          status.textContent = "Something went wrong. Please email us at support@therushb.com";
        })
        .then(validate);
    });
  }
})();
