// Outlaw Spices — site behavior

// Where the "Join the Posse" form posts. Set this to a form backend
// (Formspree, an Airtable form webhook, a Cloudflare Worker, etc.).
// While empty, signups fall back to a pre-filled email to CONTACT_EMAIL.
const SIGNUP_ENDPOINT = "";
const CONTACT_EMAIL = "hello@outlawspice.com";

document.documentElement.classList.remove("no-js");

// Logo-reveal intro (homepage). The <head> script adds .intro-on when it should play.
const intro = document.getElementById("intro");
if (intro && document.documentElement.classList.contains("intro-on")) {
  const video = intro.querySelector("video");
  const FADE_AT = 7.4; // seconds — the logo has settled to chrome by here
  let done = false;
  const finish = () => {
    if (done) return;
    done = true;
    intro.classList.add("is-out");
    document.documentElement.classList.remove("intro-on");
    document.dispatchEvent(new Event("intro:done"));
    setTimeout(() => intro.remove(), 1000);
  };
  try { sessionStorage.setItem("os-intro", "1"); } catch {}
  const portrait = window.matchMedia("(max-aspect-ratio: 1/1)").matches;
  const ext = video.canPlayType('video/webm; codecs="vp9"') ? "webm" : "mp4";
  video.src = `${portrait ? video.dataset.mobile : video.dataset.desktop}.${ext}`;
  video.addEventListener("timeupdate", () => video.currentTime >= FADE_AT && finish());
  video.addEventListener("ended", finish);
  video.addEventListener("error", finish);
  video.play().catch(finish); // autoplay blocked: go straight to the site
  intro.querySelector(".intro__skip").addEventListener("click", finish);
  document.addEventListener("keydown", (e) => e.key === "Escape" && finish());
  setTimeout(finish, 11000); // never trap anyone behind a stalled video
}

// Mobile menu
const toggle = document.querySelector(".menu-toggle");
if (toggle) {
  toggle.addEventListener("click", () => {
    const open = document.body.classList.toggle("nav-open");
    toggle.setAttribute("aria-expanded", String(open));
  });
  document.querySelectorAll(".nav a").forEach((a) =>
    a.addEventListener("click", () => {
      document.body.classList.remove("nav-open");
      toggle.setAttribute("aria-expanded", "false");
    })
  );
}

// Scroll reveal (motion.js takes over when GSAP is running)
const reveals = document.querySelectorAll(".reveal");
if (window.OS_MOTION) {
  // handled by motion.js
} else if ("IntersectionObserver" in window) {
  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          e.target.classList.add("in");
          io.unobserve(e.target);
        }
      });
    },
    { rootMargin: "0px 0px -8% 0px" }
  );
  reveals.forEach((el) => io.observe(el));
} else {
  reveals.forEach((el) => el.classList.add("in"));
}

// Homepage hero slider. Autoplay is driven by the active dot's CSS progress animation,
// so pausing that animation (hover, focus, hidden tab) also pauses the slider.
const hs = document.getElementById("hero");
if (hs && hs.classList.contains("hs")) {
  const slides = Array.from(hs.querySelectorAll(".hs__slide"));
  const dots = Array.from(hs.querySelectorAll(".hs__dot"));
  const gsap = window.OS_MOTION && window.gsap;
  let index = 0;
  let busy = false;

  const parts = (slide) => ({
    copy: slide.querySelectorAll(".hs__eyebrow, .hs__tag, .hs__name, .hs__desc, .hs__meta, .hero__ctas"),
    jar: slide.querySelector(".hs__jar"),
    ghost: slide.querySelector(".hs__ghost"),
    shadow: slide.querySelector(".hs__shadow"),
  });

  const animateIn = (slide, dir = 1, delay = 0) => {
    if (!gsap) return;
    const { copy, jar, ghost, shadow } = parts(slide);
    gsap.timeline({ delay })
      .fromTo(jar, { xPercent: 45 * dir, yPercent: 8, rotate: 16 * dir, autoAlpha: 0, scale: 0.86 },
        { xPercent: 0, yPercent: 0, rotate: 0, autoAlpha: 1, scale: 1, duration: 1.15, ease: "expo.out" }, 0)
      .fromTo(ghost, { xPercent: 18 * dir, autoAlpha: 0 }, { xPercent: 0, autoAlpha: 0.7, duration: 1.4, ease: "expo.out" }, 0.05)
      .fromTo(shadow, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.9, ease: "power3.out" }, 0.2)
      .fromTo(copy, { y: 38, autoAlpha: 0 }, { y: 0, autoAlpha: 1, duration: 0.85, ease: "power3.out", stagger: 0.07 }, 0.12);
  };

  const animateOut = (slide, dir) => {
    const { copy, jar, ghost, shadow } = parts(slide);
    return gsap.timeline()
      .to(jar, { xPercent: -40 * dir, rotate: -12 * dir, autoAlpha: 0, scale: 0.9, duration: 0.55, ease: "power3.in" }, 0)
      .to(ghost, { xPercent: -14 * dir, autoAlpha: 0, duration: 0.5, ease: "power2.in" }, 0)
      .to(shadow, { autoAlpha: 0, duration: 0.3 }, 0)
      .to(copy, { y: -22, autoAlpha: 0, duration: 0.35, ease: "power2.in", stagger: 0.03 }, 0);
  };

  const go = (next, dir) => {
    next = (next + slides.length) % slides.length;
    if (next === index || busy) return;
    if (dir === undefined) dir = next > index ? 1 : -1;
    const prev = slides[index];
    const incoming = slides[next];
    dots.forEach((d, i) => {
      d.classList.toggle("is-active", i === next);
      d.classList.toggle("is-done", i < next);
      if (i === next) d.setAttribute("aria-current", "true");
      else d.removeAttribute("aria-current");
    });
    hs.style.setProperty("--accent", incoming.dataset.accent);
    index = next;
    const swap = () => {
      prev.classList.remove("is-active");
      prev.setAttribute("aria-hidden", "true");
      incoming.classList.add("is-active");
      incoming.removeAttribute("aria-hidden");
    };
    if (!gsap) return swap();
    busy = true;
    animateOut(prev, dir).eventCallback("onComplete", () => {
      swap();
      animateIn(incoming, dir);
      busy = false;
    });
  };

  hs.querySelector(".hs__next").addEventListener("click", () => go(index + 1, 1));
  hs.querySelector(".hs__prev").addEventListener("click", () => go(index - 1, -1));
  dots.forEach((d, i) => d.addEventListener("click", () => go(i)));
  dots.forEach((d) => d.querySelector(".hs__dot-bar i").addEventListener("animationend", () => {
    if (d.classList.contains("is-active")) go(index + 1, 1);
  }));

  // Pause while the visitor is reading, interacting, or away; also hold until the intro has played.
  const pause = new Set();
  const setPaused = (reason, on) => {
    on ? pause.add(reason) : pause.delete(reason);
    hs.classList.toggle("is-paused", pause.size > 0);
  };
  const stage = hs.querySelector(".hs__stage");
  stage.addEventListener("mouseenter", () => setPaused("hover", true));
  stage.addEventListener("mouseleave", () => setPaused("hover", false));
  // Keyboard focus pauses; a mouse click on an arrow shouldn't stop autoplay.
  stage.addEventListener("focusin", (e) => e.target.matches(":focus-visible") && setPaused("focus", true));
  stage.addEventListener("focusout", () => setPaused("focus", false));
  document.addEventListener("visibilitychange", () => setPaused("hidden", document.hidden));
  if (document.documentElement.classList.contains("intro-on")) {
    setPaused("intro", true);
    document.addEventListener("intro:done", () => setPaused("intro", false), { once: true });
  }
  if ("IntersectionObserver" in window) {
    new IntersectionObserver(([e]) => setPaused("offscreen", !e.isIntersecting)).observe(hs);
  }

  // Keyboard arrows while the slider is on screen, swipe on touch.
  document.addEventListener("keydown", (e) => {
    if (pause.has("offscreen") || /input|textarea/i.test(document.activeElement.tagName)) return;
    if (e.key === "ArrowRight") go(index + 1, 1);
    if (e.key === "ArrowLeft") go(index - 1, -1);
  });
  let startX = null, startY = null;
  stage.addEventListener("touchstart", (e) => { startX = e.touches[0].clientX; startY = e.touches[0].clientY; }, { passive: true });
  stage.addEventListener("touchend", (e) => {
    if (startX === null) return;
    const dx = e.changedTouches[0].clientX - startX;
    const dy = e.changedTouches[0].clientY - startY;
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.3) go(index + (dx < 0 ? 1 : -1), dx < 0 ? 1 : -1);
    startX = null;
  }, { passive: true });

  window.OSHero = {
    enter() {
      const wrap = hs.querySelector(".hs__slides");
      wrap.style.animation = "none"; // cancel the CSS failsafe
      wrap.style.opacity = "1";
      animateIn(slides[index], 1, 0.1);
    },
  };
}

// "What's on the pit?" panels: hover/focus/tap to expand on desktop, swipe carousel on mobile.
const pits = document.getElementById("pits");
if (pits) {
  const panels = Array.from(pits.querySelectorAll(".pit"));
  const mobile = window.matchMedia("(max-width: 860px)");
  const count = document.querySelector(".pits__count b");
  const bar = document.querySelector(".pits__progress span");
  const activate = (panel) => {
    if (panel.classList.contains("is-active")) return;
    panels.forEach((p) => p.classList.toggle("is-active", p === panel));
    if (count) count.textContent = String(panels.indexOf(panel) + 1).padStart(2, "0");
  };

  panels.forEach((panel) => {
    panel.addEventListener("mouseenter", () => !mobile.matches && activate(panel));
    panel.addEventListener("focusin", () => !mobile.matches && activate(panel));
    panel.addEventListener("click", (e) => {
      if (mobile.matches || e.target.closest("a")) return;
      // First tap on a closed panel opens it; tapping an open panel goes to its blends.
      if (!panel.classList.contains("is-active")) activate(panel);
      else location.href = panel.querySelector(".pit__cta").href;
    });
  });

  // Mobile: whichever card is centered is active; progress bar follows the swipe.
  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver(
      (entries) => entries.forEach((e) => mobile.matches && e.isIntersecting && activate(e.target)),
      { root: pits, threshold: 0.6 }
    );
    panels.forEach((p) => io.observe(p));
  }
  const progress = () => {
    if (!bar) return;
    const max = pits.scrollWidth - pits.clientWidth;
    const share = 100 / panels.length;
    bar.style.width = `${share + (max > 0 ? (pits.scrollLeft / max) * (100 - share) : 0)}%`;
  };
  pits.addEventListener("scroll", progress, { passive: true });
  progress();
}

// Filter chips: <div class="filters" data-target="#grid"> + items with data-tags="a|b"
document.querySelectorAll(".filters").forEach((bar) => {
  const grid = document.querySelector(bar.dataset.target);
  if (!grid) return;
  const apply = (value) => {
    bar.querySelectorAll(".chip").forEach((c) =>
      c.setAttribute("aria-pressed", String(c.dataset.filter === value))
    );
    grid.querySelectorAll("[data-tags]").forEach((item) => {
      const tags = item.dataset.tags.split("|");
      item.classList.toggle("is-hidden", value !== "all" && !tags.includes(value));
    });
  };
  bar.addEventListener("click", (e) => {
    const chip = e.target.closest(".chip");
    if (chip) apply(chip.dataset.filter);
  });
  const fromHash = decodeURIComponent(location.hash.slice(1));
  if (fromHash && bar.querySelector(`[data-filter="${CSS.escape(fromHash)}"]`)) apply(fromHash);
});

// Product gallery
document.querySelectorAll(".gallery").forEach((g) => {
  const main = g.querySelector(".gallery__main img");
  g.querySelectorAll(".gallery__thumbs button").forEach((btn) => {
    btn.addEventListener("click", () => {
      main.src = btn.dataset.src;
      main.alt = btn.querySelector("img").alt;
      g.querySelectorAll(".gallery__thumbs button").forEach((b) => b.removeAttribute("aria-current"));
      btn.setAttribute("aria-current", "true");
    });
  });
});

// Hero video: skip autoplay for reduced-motion users and on save-data
const heroVideo = document.querySelector(".hero__media video");
if (heroVideo) {
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const saveData = navigator.connection && navigator.connection.saveData;
  if (reduce || saveData) {
    heroVideo.removeAttribute("autoplay");
    heroVideo.pause();
  }
}

// Signup
document.querySelectorAll("form.signup").forEach((form) => {
  const msg = form.parentElement.querySelector(".signup-msg");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = form.email.value.trim();
    if (!email) return;
    if (!SIGNUP_ENDPOINT) {
      const subject = encodeURIComponent("Join the Posse");
      const body = encodeURIComponent(`Count me in. Sign me up for new blends and recipes: ${email}`);
      location.href = `mailto:${CONTACT_EMAIL}?subject=${subject}&body=${body}`;
      return;
    }
    const btn = form.querySelector("button");
    btn.disabled = true;
    try {
      const res = await fetch(SIGNUP_ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({ email, source: location.pathname }),
      });
      if (!res.ok) throw new Error(res.status);
      form.reset();
      if (msg) msg.textContent = "You're in, partner. Watch your inbox.";
    } catch {
      if (msg) msg.textContent = "That didn't go through. Try again in a minute.";
    } finally {
      btn.disabled = false;
    }
  });
});
