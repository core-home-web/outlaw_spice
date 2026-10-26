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
