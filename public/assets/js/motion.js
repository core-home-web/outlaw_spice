// Outlaw Spices — GSAP motion: page transitions, text reveals, scroll animations.
// Runs only when the <head> script added .motion (i.e. not prefers-reduced-motion).
// If GSAP fails to load, CSS fallbacks in site.css un-hide everything after a beat.

(() => {
  const root = document.documentElement;
  if (!root.classList.contains("motion") || !window.gsap || !window.ScrollTrigger) return;

  const { gsap, ScrollTrigger } = window;
  const SplitText = window.SplitText;
  gsap.registerPlugin(ScrollTrigger, ...(SplitText ? [SplitText] : []));
  window.OS_MOTION = true; // tells site.js to skip its basic reveal

  const ease = "power3.out";
  const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));
  const show = (el) => {
    el.style.animation = "none";
    el.style.visibility = "visible";
  };

  // ------------------------------------------------------------ page transitions
  const pt = document.querySelector(".pt");
  const panel = pt && pt.querySelector(".pt__panel");
  const ptLogo = pt && pt.querySelector(".pt__logo");
  let arrived = Promise.resolve();

  if (pt && root.classList.contains("pt-in")) {
    // We got here through a transition: the panel is covering the page. Wipe it away.
    try { sessionStorage.removeItem("os-pt"); } catch {}
    arrived = new Promise((resolve) => {
      pt.style.animation = ptLogo.style.animation = "none"; // cancel the CSS failsafe
      gsap.set(pt, { visibility: "visible" });
      gsap.timeline({
        delay: 0.05,
        onComplete: () => {
          root.classList.remove("pt-in");
          gsap.set(pt, { clearProps: "all" });
          gsap.set([panel, ptLogo], { clearProps: "all" });
          resolve();
        },
      })
        .to(ptLogo, { autoAlpha: 0, y: -20, duration: 0.3, ease: "power2.in", delay: 0.15 })
        .to(panel, { scaleY: 0, transformOrigin: "50% 0%", duration: 0.7, ease: "expo.inOut" }, "-=0.1");
      // the page content rises in under the wipe
      gsap.from("main", { y: 40, duration: 1, ease, delay: 0.3, clearProps: "transform" });
    });
  }

  const isInternal = (a) => {
    if (!a || a.target === "_blank" || a.hasAttribute("download")) return false;
    const url = new URL(a.href, location.href);
    if (url.origin !== location.origin) return false;
    if (url.pathname === location.pathname && url.search === location.search) return false; // same-page / hash links
    return true;
  };

  if (pt) {
    let leaving = false;
    document.addEventListener("click", (e) => {
      if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      const a = e.target.closest("a[href]");
      if (!isInternal(a) || leaving) return;
      e.preventDefault();
      leaving = true;
      const go = () => { location.href = a.href; };
      try { sessionStorage.setItem("os-pt", "1"); } catch {}
      gsap.set(pt, { visibility: "visible" });
      gsap.timeline({ onComplete: go })
        .fromTo(panel, { scaleY: 0, transformOrigin: "50% 100%" }, { scaleY: 1, duration: 0.6, ease: "expo.inOut" })
        .fromTo(ptLogo, { autoAlpha: 0, y: 20 }, { autoAlpha: 1, y: 0, duration: 0.3, ease }, 0.25)
        .to({}, { duration: 0.1 }); // let the logo land before leaving
      setTimeout(go, 1200); // never strand a click
    });

    // Back/forward cache restores the page mid-transition: reset it.
    window.addEventListener("pageshow", (e) => {
      if (!e.persisted) return;
      leaving = false;
      root.classList.remove("pt-in");
      gsap.set([pt, panel, ptLogo], { clearProps: "all" });
    });
  }

  // ------------------------------------------------------------ text reveals
  const splitHeading = (el, { delay = 0, scroll = true, stagger = 0.06 } = {}) => {
    if (!SplitText) return show(el);
    const split = SplitText.create(el, { type: "lines,words", mask: "lines", linesClass: "split-line", autoSplit: true,
      onSplit(self) {
        show(el);
        return gsap.from(self.words, {
          yPercent: 115,
          rotate: 4,
          duration: 1,
          ease: "power4.out",
          stagger,
          delay,
          scrollTrigger: scroll ? { trigger: el, start: "top 88%", once: true } : undefined,
        });
      },
    });
    return split;
  };

  const scriptReveal = (el, opts = {}) =>
    gsap.fromTo(el, { clipPath: "inset(-20% 100% -20% 0)" }, {
      clipPath: "inset(-20% 0% -20% 0)", duration: 1.1, ease: "power2.inOut", ...opts,
    });

  const runHero = () => {
    const hero = document.querySelector(".hero");
    if (!hero) return;
    const tl = gsap.timeline();
    const script = hero.querySelector(".hero__script");
    const heading = hero.querySelector(".display");
    if (script) tl.add(scriptReveal(script), 0);
    if (heading) splitHeading(heading, { delay: 0.15, scroll: false, stagger: 0.07 });
    tl.from(hero.querySelectorAll(".lede, .hero__ctas > *"), { y: 30, autoAlpha: 0, duration: 0.9, ease, stagger: 0.1 }, 0.55);
    tl.from(".strip", { yPercent: 120, rotate: 0, duration: 1, ease: "expo.out" }, 0.4);
  };

  const initText = () => {
    // Every big headline except the hero (which waits for the intro).
    $$(".display, .h2, .pdp h1").forEach((el) => {
      if (el.closest(".hero")) return;
      const inFirstScreen = el.getBoundingClientRect().top < innerHeight;
      splitHeading(el, { scroll: !inFirstScreen, delay: inFirstScreen ? 0.25 : 0 });
    });

    $$(".pdp__tagline, .page-hero .script, .notfound .script").forEach((el) => scriptReveal(el, { delay: 0.2 }));

    $$(".eyebrow").forEach((el) => {
      if (el.closest(".hero")) return;
      gsap.from(el, {
        autoAlpha: 0, x: -16, duration: 0.8, ease,
        scrollTrigger: { trigger: el, start: "top 90%", once: true },
      });
    });

    const heroStart = () => runHero();
    if (root.classList.contains("intro-on")) document.addEventListener("intro:done", heroStart, { once: true });
    else heroStart();
  };

  // ------------------------------------------------------------ scroll animations
  const initScroll = () => {
    // Hero: media drifts and zooms, copy lifts away as you scroll past.
    const hero = document.querySelector(".hero");
    if (hero) {
      const st = { trigger: hero, start: "top top", end: "bottom top", scrub: true };
      gsap.to(".hero__media", { yPercent: 18, scale: 1.08, ease: "none", scrollTrigger: st });
      gsap.to(".hero .wrap", { yPercent: -12, autoAlpha: 0.2, ease: "none", scrollTrigger: { ...st, start: "40% top" } });
    }

    // Inner-page hero backgrounds parallax.
    $$(".page-hero__bg, .recipe-hero__bg").forEach((bg) => {
      gsap.fromTo(bg, { scale: 1.12 }, { scale: 1, duration: 1.6, ease });
      gsap.to(bg, { yPercent: 15, ease: "none", scrollTrigger: { trigger: bg.parentElement, start: "top top", end: "bottom top", scrub: true } });
    });

    // Marquee leans into your scroll speed.
    const strip = document.querySelector(".strip__track");
    if (strip) {
      const skew = gsap.quickTo(strip, "skewX", { duration: 0.5, ease: "power3" });
      ScrollTrigger.create({
        onUpdate: (self) => skew(gsap.utils.clamp(-12, 12, self.getVelocity() / -250)),
      });
    }

    // Image panels: clip-reveal on entry, then parallax inside the frame.
    $$(".split__media").forEach((box) => {
      const img = box.querySelector("img");
      gsap.fromTo(box, { clipPath: "inset(12% 8% 12% 8%)", autoAlpha: 0 }, {
        clipPath: "inset(0% 0% 0% 0%)", autoAlpha: 1, duration: 1.3, ease: "expo.out",
        scrollTrigger: { trigger: box, start: "top 85%", once: true },
      });
      if (img) {
        gsap.fromTo(img, { yPercent: -6, scale: 1.14 }, {
          yPercent: 6, scale: 1.14, ease: "none",
          scrollTrigger: { trigger: box, start: "top bottom", end: "bottom top", scrub: true },
        });
      }
    });

    $$(".stamp").forEach((s) =>
      gsap.fromTo(s, { rotate: -40, scale: 0.6, autoAlpha: 0 }, {
        rotate: -10, scale: 1, autoAlpha: 1, duration: 1, ease: "back.out(2)",
        scrollTrigger: { trigger: s, start: "top 92%", once: true },
      })
    );

    // Copy blocks next to images.
    $$(".split > .reveal:not(.split__media)").forEach((block) => {
      gsap.from(block.querySelectorAll(":scope > p, :scope > .checks li, :scope > .btn, :scope > .link-arrow"), {
        y: 30, autoAlpha: 0, duration: 0.9, ease, stagger: 0.08,
        scrollTrigger: { trigger: block, start: "top 80%", once: true },
      });
    });

    // Cards (products, recipes) come in as staggered batches.
    gsap.set(".card", { autoAlpha: 0, y: 60 });
    ScrollTrigger.batch(".card", {
      start: "top 92%",
      once: true,
      onEnter: (batch) => gsap.to(batch, { autoAlpha: 1, y: 0, duration: 0.9, ease, stagger: 0.1, overwrite: true }),
    });
    // Re-check after filtering shows previously hidden cards.
    $$(".filters").forEach((bar) => bar.addEventListener("click", () => requestAnimationFrame(() => {
      ScrollTrigger.refresh();
      $$(".card").forEach((c) => {
        if (!c.classList.contains("is-hidden") && c.getBoundingClientRect().top < innerHeight) gsap.to(c, { autoAlpha: 1, y: 0, duration: 0.6, ease });
      });
    })));

    // Protein picker tiles wipe up one by one.
    const picker = document.querySelector(".picker");
    if (picker) {
      gsap.from(picker.children, {
        clipPath: "inset(100% 0 0 0)", duration: 1.1, ease: "expo.out", stagger: 0.09,
        scrollTrigger: { trigger: picker, start: "top 85%", once: true },
      });
    }

    // Temperatures count up; stats and values rise in.
    $$(".temps, .values, .facts, .recipe-stats").forEach((group) => {
      gsap.from(group.children, {
        y: 40, autoAlpha: 0, duration: 0.8, ease, stagger: 0.08,
        scrollTrigger: { trigger: group, start: "top 88%", once: true },
      });
    });
    $$(".temp__num, .value .num").forEach((el) => {
      const node = el.firstChild;
      const target = parseInt(node && node.textContent, 10);
      if (!node || node.nodeType !== 3 || Number.isNaN(target)) return;
      const pad = node.textContent.trim().length;
      const counter = { v: 0 };
      gsap.to(counter, {
        v: target, duration: 1.6, ease: "power2.out",
        scrollTrigger: { trigger: el, start: "top 90%", once: true },
        onUpdate: () => { node.textContent = String(Math.round(counter.v)).padStart(pad, "0"); },
      });
    });

    // Recipe page: ingredients and steps.
    $$(".ingredients li, .steps li, .howto li").forEach((li) =>
      gsap.from(li, {
        x: -24, autoAlpha: 0, duration: 0.7, ease,
        scrollTrigger: { trigger: li, start: "top 92%", once: true },
      })
    );
    $$(".tip, .blend-callout").forEach((el) =>
      gsap.from(el, { y: 30, autoAlpha: 0, duration: 0.9, ease, scrollTrigger: { trigger: el, start: "top 92%", once: true } })
    );

    // Product gallery settles in.
    const gallery = document.querySelector(".gallery");
    if (gallery) {
      gsap.from(".gallery__main", { scale: 0.94, autoAlpha: 0, duration: 1.1, ease: "expo.out", delay: 0.15 });
      gsap.from(".gallery__thumbs > *", { y: 20, autoAlpha: 0, duration: 0.6, ease, stagger: 0.07, delay: 0.45 });
      gsap.from(".pdp__weight, .pdp__desc, .cta-row > *, .badges > *", { y: 24, autoAlpha: 0, duration: 0.8, ease, stagger: 0.06, delay: 0.5 });
    }

    // Posse: background slowly pushes in, signup rises.
    const posse = document.querySelector(".posse");
    if (posse) {
      gsap.fromTo(".posse__bg", { scale: 1.25 }, { scale: 1, ease: "none", scrollTrigger: { trigger: posse, start: "top bottom", end: "bottom top", scrub: true } });
      gsap.from(".posse .lede, .posse .signup", { y: 30, autoAlpha: 0, duration: 0.9, ease, stagger: 0.12, scrollTrigger: { trigger: posse, start: "top 70%", once: true } });
    }

    // Footer wordmark slides across as you reach the bottom.
    const word = document.querySelector(".footer-word");
    if (word) {
      gsap.fromTo(word, { xPercent: 12 }, { xPercent: -4, ease: "none", scrollTrigger: { trigger: word, start: "top bottom", end: "bottom bottom", scrub: true } });
    }

    // Header tucks away on scroll down, returns on scroll up.
    const header = document.querySelector(".site-header");
    if (header) {
      const hide = gsap.to(header, { yPercent: -100, duration: 0.35, ease: "power2.inOut", paused: true });
      ScrollTrigger.create({
        start: 200,
        onUpdate: (self) => {
          if (document.body.classList.contains("nav-open")) return hide.reverse();
          self.direction === 1 ? hide.play() : hide.reverse();
        },
        onLeaveBack: () => hide.reverse(),
      });
    }
  };

  // Non-text motion can start right away; split text waits for web fonts so lines measure right.
  initScroll();
  const fontsReady = document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve();
  Promise.all([fontsReady, arrived.then(() => null)]).then(() => {
    initText();
    ScrollTrigger.refresh();
  });
  // Images loading late change layout; keep triggers honest.
  window.addEventListener("load", () => ScrollTrigger.refresh());
})();
