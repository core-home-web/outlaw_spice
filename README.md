# Outlaw Spices: website

Static BBQ brand site deployed on Cloudflare Workers (static assets).

## Layout

| Path | What it is |
| --- | --- |
| `public/` | **The deployed site.** Generated HTML + `assets/` (CSS, JS, WebP images, video). |
| `data/products.json` | The 11 blends: name, label tagline, net weight, heat, flavor, copy, how-to. `price` is `null` (hidden) until set, e.g. `"$12.99"`. |
| | Set `"featured": true` on the blends you want in the homepage hero slider (order follows the file). |
| `data/recipes.json` | Recipes, each tied to a blend and a photo in `public/assets/img/`. |
| `build.py` | Renders every page in `public/` from the JSON. |
| `tools/optimize_images.py` | Turns originals in `brand-assets/` into web-sized WebP in `public/assets/img/`. |
| `brand-assets/` | Full-resolution photo, logo and video library (not deployed). |
| `wrangler.jsonc` | Deploys only `public/`. |

## Edit content

```bash
# edit data/products.json or data/recipes.json, then:
python3 build.py
git add -A && git commit -m "Update content" && git push
```

Cloudflare's deploy command (`npx wrangler deploy`) publishes `public/` as committed, so
always run `build.py` before you commit.

New photos: drop the original into `brand-assets/photos/`, add it to `PHOTOS` in
`tools/optimize_images.py`, run `python3 tools/optimize_images.py`, then use its name
as a recipe `image`.

## Share images (Open Graph)

Every page has a branded 1200x630 share card in `public/assets/og/` (blend, recipe and
page designs), plus meta title/description and Open Graph + Twitter tags. `build.py` writes
the card list to `data/og-cards.json`; render the cards after changing products or recipes:

```bash
python3 build.py && node tools/make_og.cjs     # needs Playwright + Chromium
```

Share URLs use `SITE_URL` in `build.py` (`https://outlawspice.com`), so that domain must
point at this Cloudflare Worker for the images to show up when links are shared.

## Email signups ("Join the Posse")

Set `SIGNUP_ENDPOINT` at the top of `public/assets/js/site.js` to a form backend
(Formspree, an Airtable/Make webhook, a Worker). Until then the form opens a
pre-filled email to `hello@outlawspice.com`.

## Homepage intro

The fire logo-reveal (`public/assets/video/intro*.{mp4,webm}`) plays full-screen once per
browser session on the homepage, then fades into the site. It's skippable, uses a portrait
cut on phones, and is skipped for visitors with reduced motion turned on.

## Motion (GSAP)

`public/assets/js/motion.js` drives page transitions, headline text reveals and scroll
animations using GSAP 3.13 (self-hosted in `public/assets/vendor/`). It's off for visitors with
reduced motion turned on, and if GSAP fails to load, CSS failsafes show all content after a moment.

## Local preview

```bash
npx wrangler dev   # serves public/ with the same routing as production
```
