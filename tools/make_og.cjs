// Render 1200x630 Open Graph share cards for every page.
//
//   python3 build.py            # writes data/og-cards.json
//   node tools/make_og.cjs      # renders public/assets/og/<key>.jpg
//
// Needs Playwright with Chromium (`npm i -g playwright && npx playwright install chromium`)
// and network access to Google Fonts, so the cards use the site's typefaces.

const fs = require("fs");
const os = require("os");
const path = require("path");
const { chromium } = require("playwright");

const ROOT = path.resolve(__dirname, "..");
const PUBLIC = path.join(ROOT, "public");
const OUT = path.join(PUBLIC, "assets", "og");
const cards = JSON.parse(fs.readFileSync(path.join(ROOT, "data", "og-cards.json"), "utf8"));
const only = process.argv.slice(2); // optional: render just these keys

const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const img = (rel) => `assets/img/${rel}.webp`;
const jar = (slug) => `assets/img/products/${slug}-cutout-1400.webp`;
const heat = (n) => Array.from({ length: 5 }, (_, i) => `<i class="${i < n ? "on" : ""}"></i>`).join("");

const FONTS = "https://fonts.googleapis.com/css2?family=Anton&family=Caveat:wght@700&family=Inter:wght@500;600&family=Zilla+Slab:wght@700&display=block";

const CSS = `
* { box-sizing: border-box; margin: 0; }
html, body { width: 1200px; height: 630px; overflow: hidden; background: #0f0d0c; color: #f3ead9; font-family: Inter, sans-serif; }
.card { position: relative; width: 1200px; height: 630px; overflow: hidden; isolation: isolate; border-bottom: 8px solid var(--accent); }
.bg { position: absolute; inset: 0; z-index: -3; width: 100%; height: 100%; object-fit: cover; }
.shade { position: absolute; inset: 0; z-index: -2; }
.glow { position: absolute; z-index: -1; border-radius: 50%; filter: blur(30px); }
.logo { position: absolute; top: 46px; left: 64px; width: 210px; }
.foot { position: absolute; left: 64px; right: 64px; bottom: 34px; display: flex; justify-content: space-between; align-items: center;
  font-family: "Zilla Slab", serif; font-weight: 700; text-transform: uppercase; letter-spacing: 0.18em; font-size: 17px; color: rgba(243,234,217,0.72); }
.foot b { color: #f3ead9; }
.eyebrow { display: flex; align-items: center; gap: 14px; font-family: "Zilla Slab", serif; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.24em; font-size: 20px; color: var(--accent); }
.eyebrow::before { content: ""; width: 40px; height: 3px; background: currentColor; }
.script { font-family: Caveat, cursive; font-weight: 700; color: var(--accent); line-height: 1; display: inline-block; transform: rotate(-3deg); transform-origin: left; }
.title { font-family: Anton, Impact, sans-serif; text-transform: uppercase; line-height: 0.97; letter-spacing: 0.005em; text-shadow: 0 6px 30px rgba(0,0,0,0.5); }
.title em { font-style: normal; color: var(--accent); }
.copy { position: absolute; left: 64px; top: 150px; bottom: 96px; display: flex; flex-direction: column; justify-content: center; gap: 16px; }
.meta { display: flex; align-items: center; gap: 22px; font-family: "Zilla Slab", serif; font-weight: 700; text-transform: uppercase; letter-spacing: 0.14em; font-size: 19px; color: rgba(243,234,217,0.8); }
.heat { display: inline-flex; gap: 5px; }
.heat i { width: 14px; height: 21px; border-radius: 50% 50% 45% 45% / 60% 60% 40% 40%; background: rgba(243,234,217,0.2); }
.heat i.on { background: linear-gradient(180deg, #ffb347, #d8401f); }
.jar { position: absolute; filter: drop-shadow(0 26px 30px rgba(0,0,0,0.65)); }
.ghost { position: absolute; font-family: Anton, sans-serif; text-transform: uppercase; line-height: 0.8; white-space: nowrap;
  color: transparent; -webkit-text-stroke: 2px var(--accent); opacity: 0.35; }
.stats { display: flex; gap: 0; margin-top: 6px; border: 1px solid rgba(243,234,217,0.18); border-radius: 6px; width: fit-content; background: rgba(15,13,12,0.55); }
.stats div { padding: 12px 22px; border-right: 1px solid rgba(243,234,217,0.18); }
.stats div:last-child { border-right: 0; }
.stats small { display: block; font-family: "Zilla Slab", serif; font-weight: 700; text-transform: uppercase; letter-spacing: 0.16em; font-size: 14px; color: rgba(243,234,217,0.65); }
.stats b { font-family: Anton, sans-serif; font-weight: 400; font-size: 30px; }
`;

const FOOT = `<div class="foot"><span><b>outlawspice.com</b></span><span>Gluten free · Kosher certified</span></div>`;
const LOGO = `<img class="logo" src="assets/img/logo-white.png" alt="">`;

function product(c) {
  const first = c.name.split(" ")[0].replace(/['’]/g, "");
  return `<div class="card" style="--accent:${c.accent}">
    <img class="bg" src="${img("flame-grill-1800")}">
    <div class="shade" style="background: linear-gradient(90deg, rgba(15,13,12,0.96) 0%, rgba(15,13,12,0.86) 48%, rgba(15,13,12,0.55) 100%)"></div>
    <div class="glow" style="right: 90px; top: 90px; width: 420px; height: 420px; background: ${c.accent}; opacity: 0.35"></div>
    <div style="position: absolute; left: 640px; right: 0; top: 0; bottom: 0; overflow: hidden; z-index: -1"><span class="ghost" style="left: 0; top: 170px; font-size: 260px">${esc(first)}</span></div>
    <img class="jar" src="${jar(c.slug)}" style="right: 160px; top: 40px; height: 505px">
    ${LOGO}
    <div class="copy" style="width: 640px">
      <span class="script" style="font-size: 60px">${esc(c.tagline)}</span>
      <h1 class="title fit" data-max="250" style="font-size: 104px">${esc(c.name)}</h1>
      <div class="meta"><span class="heat">${heat(c.heat)}</span><span>Net wt. ${esc(c.weight)}</span></div>
    </div>
    ${FOOT}
  </div>`;
}

function recipe(c) {
  return `<div class="card" style="--accent:${c.accent}">
    <img class="bg" src="${img(c.image)}" style="left: 380px; width: 820px">
    <div class="shade" style="background: linear-gradient(90deg, #0f0d0c 0%, #0f0d0c 34%, rgba(15,13,12,0.75) 52%, rgba(15,13,12,0.05) 80%)"></div>
    <img class="jar" src="${jar(c.blend)}" style="right: 80px; bottom: 82px; height: 280px; transform: rotate(6deg)">
    ${LOGO}
    <div class="copy" style="width: 700px">
      <span class="eyebrow">Recipe · ${esc(c.method)} · ${esc(c.category)}</span>
      <h1 class="title fit" data-max="230" style="font-size: 100px">${esc(c.title)}</h1>
      <span class="script" style="font-size: 46px">with ${esc(c.blend_name)}</span>
      <div class="stats"><div><small>Prep</small><b>${esc(c.prep)}</b></div><div><small>Cook</small><b>${esc(c.cook)}</b></div><div><small>Serves</small><b>${esc(c.serves)}</b></div></div>
    </div>
    ${FOOT}
  </div>`;
}

function page(c) {
  const jars = (c.jars || [])
    .map((s, i) => {
      const pos = [
        "right: 300px; top: 120px; height: 430px; transform: rotate(-8deg)",
        "right: 70px; top: 120px; height: 430px; transform: rotate(8deg)",
        "right: 175px; top: 70px; height: 500px",
      ][i];
      return `<img class="jar" src="${jar(s)}" style="${pos}">`;
    })
    .join("");
  return `<div class="card" style="--accent:#e8742a">
    <img class="bg" src="${img(c.bg)}">
    <div class="shade" style="background: linear-gradient(90deg, rgba(15,13,12,0.95) 0%, rgba(15,13,12,0.8) ${c.jars ? 52 : 45}%, rgba(15,13,12,${c.jars ? 0.6 : 0.2}) 100%)"></div>
    ${c.jars ? '<div class="glow" style="right: 120px; top: 120px; width: 460px; height: 400px; background: #e8742a; opacity: 0.3"></div>' : ""}
    ${jars}
    ${LOGO}
    <div class="copy" style="width: ${c.jars ? 640 : 860}px">
      <span class="eyebrow">${esc(c.eyebrow)}</span>
      <h1 class="title fit" data-max="260" style="font-size: 120px">${esc(c.headline)} <em>${esc(c.accent)}</em></h1>
      <p style="font-size: 26px; font-weight: 500; color: rgba(243,234,217,0.85); max-width: 600px; line-height: 1.35">${esc(c.sub)}</p>
    </div>
    ${FOOT}
  </div>`;
}

const RENDER = { product, recipe, page };

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
  const pg = await ctx.newPage();
  for (const c of cards) {
    if (only.length && !only.includes(c.key)) continue;
    const html = `<!doctype html><html><head><meta charset="utf-8"><base href="file://${PUBLIC}/">
      <link rel="stylesheet" href="${FONTS}"><style>${CSS}</style></head><body>${RENDER[c.kind](c)}</body></html>`;
    const file = path.join(os.tmpdir(), `og-render-${c.key}.html`);
    fs.writeFileSync(file, html);
    await pg.goto(`file://${file}`, { waitUntil: "load" });
    await pg.evaluate(() => Promise.all(['20px Anton', '700 20px Caveat', '700 20px "Zilla Slab"', '500 20px Inter'].map((f) => document.fonts.load(f))));
    await pg.evaluate(() => document.fonts.ready);
    // Shrink long titles until they fit their box.
    await pg.evaluate(() => {
      document.querySelectorAll(".fit").forEach((el) => {
        let size = parseFloat(getComputedStyle(el).fontSize);
        while (el.offsetHeight > +el.dataset.max && size > 40) el.style.fontSize = `${(size -= 2)}px`;
      });
    });
    const fonts = await pg.evaluate(() => ['20px Anton', '700 20px Caveat', '700 20px "Zilla Slab"'].every((f) => document.fonts.check(f)));
    if (!fonts) throw new Error(`fonts did not load for ${c.key}`);
    await pg.screenshot({ path: path.join(OUT, `${c.key}.jpg`), type: "jpeg", quality: 86 });
    fs.unlinkSync(file);
    console.log("og", c.key);
  }
  await browser.close();
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
