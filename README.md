# Outlaw Spices: website

Static BBQ brand site deployed on Cloudflare Workers (static assets).

## Layout

| Path | What it is |
| --- | --- |
| `public/` | **The deployed site.** Generated HTML + `assets/` (CSS, JS, WebP images, video). |
| `data/products.json` | The 11 blends: name, label tagline, net weight, heat, flavor, copy, how-to. `price` is `null` (hidden) until set, e.g. `"$12.99"`. |
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

## Email signups ("Join the Posse")

Set `SIGNUP_ENDPOINT` at the top of `public/assets/js/site.js` to a form backend
(Formspree, an Airtable/Make webhook, a Worker). Until then the form opens a
pre-filled email to `hello@outlawspice.com`.

## Homepage intro

The fire logo-reveal (`public/assets/video/intro*.{mp4,webm}`) plays full-screen once per
browser session on the homepage, then fades into the site. It's skippable, uses a portrait
cut on phones, and is skipped for visitors with reduced motion turned on.

## Local preview

```bash
npx wrangler dev   # serves public/ with the same routing as production
```
