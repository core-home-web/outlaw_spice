"""Generate the Outlaw Spices static site into public/.

Content lives in data/products.json and data/recipes.json.
Run:  python3 build.py
Then commit public/ — Cloudflare deploys that folder as-is (see wrangler.jsonc).
"""
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "public"
SITE_URL = "https://outlawspice.com"
GA_ID = "G-LXRS43EWS6"

PRODUCTS = json.loads((ROOT / "data/products.json").read_text(encoding="utf-8"))
RECIPES = json.loads((ROOT / "data/recipes.json").read_text(encoding="utf-8"))
BY_SLUG = {p["slug"]: p for p in PRODUCTS}

# "What's on the pit" buckets used by the filters, from each blend's best_on list.
PITS = {
    "Beef": {"Beef", "Brisket", "Burgers", "Game", "Jerky"},
    "Pork": {"Pork", "Pork Shoulder", "Ribs", "Chops"},
    "Poultry": {"Chicken", "Wings", "Turkey"},
    "Seafood": {"Shrimp", "Salmon", "Seafood"},
    "Veggies": {"Veggies", "Potatoes"},
}
HEAT_WORDS = {1: "Mild", 2: "Warm", 3: "Medium", 4: "Hot", 5: "Fire"}


def pits_for(p):
    return [pit for pit, cuts in PITS.items() if cuts & set(p["best_on"])]


def short(p):
    return p.get("short_name", p["name"])


def heat(n, label=True):
    drops = "".join(f'<i class="{"on" if i <= n else ""}"></i>' for i in range(1, 6))
    word = f'<span class="heat-label">{HEAT_WORDS[n]}</span>' if label else ""
    return f'<span class="heat" title="Heat {n} of 5" aria-label="Heat level {n} of 5">{drops}{word}</span>'


def img(name, alt, sizes="100vw", widths=(900, 1800), cls="", eager=False):
    srcset = ", ".join(f"/assets/img/{name}-{w}.webp {w}w" for w in widths)
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    c = f' class="{cls}"' if cls else ""
    return (f'<img{c} src="/assets/img/{name}-{widths[0]}.webp" srcset="{srcset}" sizes="{sizes}" '
            f'alt="{escape(alt)}" {load} decoding="async">')


# ---------------------------------------------------------------- layout

FONTS = ("https://fonts.googleapis.com/css2?family=Anton&family=Caveat:wght@700"
         "&family=Inter:wght@400;500;600&family=Zilla+Slab:wght@500;700&display=swap")

NAV = [("/products/", "Shop Blends"), ("/recipes/", "Recipes"), ("/#pit-guide", "Pit Guide"), ("/about", "Our Story")]


def layout(*, title, description, body, path, active="", image="/assets/img/lineup-1800.webp", jsonld=None, intro=False):
    full_title = title if "Outlaw Spices" in title else f"{title} | Outlaw Spices"
    nav = "".join(
        f'<a href="{href}"{" aria-current=page" if label == active else ""}>{label}</a>' for href, label in NAV
    )
    ld = f'<script type="application/ld+json">{json.dumps(jsonld)}</script>' if jsonld else ""
    intro_head, intro_body = (INTRO_HEAD, INTRO_BODY) if intro else ("", "")
    return f"""<!doctype html>
<html lang="en" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(full_title)}</title>
<meta name="description" content="{escape(description)}">
<link rel="canonical" href="{SITE_URL}{path}">
<meta name="theme-color" content="#0f0d0c">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Outlaw Spices">
<meta property="og:title" content="{escape(full_title)}">
<meta property="og:description" content="{escape(description)}">
<meta property="og:url" content="{SITE_URL}{path}">
<meta property="og:image" content="{SITE_URL}{image}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="/assets/css/site.css">
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{GA_ID}');</script>
{ld}
{intro_head}
</head>
<body>
{intro_body}
<a class="skip" href="#main">Skip to content</a>
<div class="announce">New here? <a href="#posse">Join the Posse</a> for first dibs on new blends &amp; pit-tested recipes</div>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="/" aria-label="Outlaw Spices home"><img src="/assets/img/logo-white.webp" alt="Outlaw Spices" width="150" height="67"></a>
    <button class="menu-toggle" aria-label="Menu" aria-expanded="false" aria-controls="nav"><span></span><span></span><span></span></button>
    <nav class="nav" id="nav" aria-label="Main">{nav}<a class="btn" href="#posse">Join the Posse</a></nav>
  </div>
</header>
<main id="main">
{body}
{posse()}
</main>
{footer()}
<script src="/assets/js/site.js" defer></script>
</body>
</html>
"""


# Logo-reveal intro, homepage only. The head script decides before first paint
# (once per session, never for reduced-motion) so the page never flashes underneath.
INTRO_HEAD = """<script>try{if(!sessionStorage.getItem('os-intro')&&!matchMedia('(prefers-reduced-motion: reduce)').matches)document.documentElement.classList.add('intro-on')}catch(e){}</script>"""
INTRO_BODY = """<div class="intro" id="intro">
  <video muted playsinline preload="auto" aria-hidden="true" data-desktop="/assets/video/intro" data-mobile="/assets/video/intro-mobile"></video>
  <button class="intro__skip" type="button">Skip intro <span aria-hidden="true">→</span></button>
</div>"""


def posse():
    return f"""
<section class="posse" id="posse" aria-labelledby="posse-title">
  <div class="posse__bg">{img("flame-grill", "", widths=(900, 1800))}</div>
  <div class="wrap">
    <span class="eyebrow">The Outlaw Posse</span>
    <h2 class="h2" id="posse-title" style="margin-top:16px">Ride With <span class="ember">The Posse</span></h2>
    <p class="lede">New blends, limited drops and pit-tested recipes, straight to your inbox. No spam, just smoke.</p>
    <form class="signup" novalidate>
      <label class="sr-only" for="email-posse">Email address</label>
      <input id="email-posse" type="email" name="email" placeholder="Your email, partner" autocomplete="email" required>
      <button class="btn" type="submit">Saddle Up</button>
    </form>
    <p class="signup-msg" role="status"></p>
  </div>
</section>"""


def footer():
    blends = "".join(f'<li><a href="/products/{p["slug"]}">{escape(short(p))}</a></li>' for p in PRODUCTS[:6])
    return f"""
<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <img src="/assets/img/logo-white.webp" alt="Outlaw Spices" width="170" height="75" loading="lazy">
        <p>Bold BBQ rubs &amp; seasonings for backyard pitmasters, tailgate legends and anyone who cooks over fire. Seasoned like no other.</p>
      </div>
      <div><h4>Blends</h4><ul>{blends}<li><a href="/products/">All 11 blends →</a></li></ul></div>
      <div><h4>Cook</h4><ul>
        <li><a href="/recipes/">All recipes</a></li>
        <li><a href="/#pit-guide">Pit temp guide</a></li>
        <li><a href="/recipes/roadhouse-smoked-brisket">Smoked brisket</a></li>
        <li><a href="/recipes/kansas-city-sticky-ribs">Sticky ribs</a></li>
      </ul></div>
      <div><h4>Outlaw</h4><ul>
        <li><a href="/about">Our story</a></li>
        <li><a href="#posse">Join the Posse</a></li>
        <li><a href="mailto:hello@outlawspice.com">hello@outlawspice.com</a></li>
      </ul></div>
    </div>
    <div class="footer-word" aria-hidden="true">Outlaw Spices</div>
    <div class="footer-bottom"><span>© 2026 Outlaw Spices. All rights reserved.</span><span>Gluten free · Kosher certified · Seasoned like no other</span></div>
  </div>
</footer>"""


# ---------------------------------------------------------------- components

def product_card(p, sizes="(max-width: 600px) 100vw, 300px"):
    tags = "|".join(["all", *pits_for(p), *p["profile"]])
    return f"""<a class="card product-card reveal" href="/products/{p['slug']}" data-tags="{escape(tags)}" style="--accent:{p['accent']}">
  <div class="product-card__img">
    <span class="badge-heat">{heat(p['heat'], label=False)}</span>
    <img src="/assets/img/products/{p['slug']}-1-480.webp" srcset="/assets/img/products/{p['slug']}-1-480.webp 480w, /assets/img/products/{p['slug']}-1.webp 900w" sizes="{sizes}" alt="{escape(p['name'])} jar" loading="lazy" decoding="async" width="480" height="480">
  </div>
  <div class="product-card__body">
    <span class="product-card__tag">{escape(p['tagline'])}</span>
    <span class="product-card__name">{escape(p['name'])}</span>
    <span class="muted" style="font-size:.92rem">{escape(p['short'])}</span>
    <span class="product-card__meta"><span>{escape(" · ".join(p['best_on']))}</span><span class="link-arrow">View <span>→</span></span></span>
  </div>
</a>"""


def recipe_card(r):
    blend = BY_SLUG[r["blend"]]
    tags = "|".join(["all", r["category"], r["method"]])
    return f"""<a class="card recipe-card reveal" href="/recipes/{r['slug']}" data-tags="{escape(tags)}">
  <div class="recipe-card__img">{img(r['image'], r['title'], sizes="(max-width: 700px) 100vw, 400px")}<span class="recipe-card__pill">{escape(r['method'])} · {escape(r['category'])}</span></div>
  <div class="recipe-card__body">
    <span class="product-card__tag" style="--accent:{blend['accent']}">with {escape(short(blend))}</span>
    <h3 class="recipe-card__title">{escape(r['title'])}</h3>
    <p>{escape(r['summary'])}</p>
    <div class="recipe-card__meta"><span>Prep <b>{escape(r['prep'])}</b></span><span>Cook <b>{escape(r['cook'])}</b></span><span>Serves <b>{r['serves']}</b></span></div>
  </div>
</a>"""


def chips(target, options):
    btns = '<button class="chip" data-filter="all" aria-pressed="true">All</button>'
    btns += "".join(f'<button class="chip" data-filter="{escape(o)}" aria-pressed="false">{escape(o)}</button>' for o in options)
    return f'<div class="filters" data-target="{target}" role="group" aria-label="Filter">{btns}</div>'


# ---------------------------------------------------------------- pages

def home():
    featured = [p for p in PRODUCTS if p.get("featured")]
    strip_words = ["Gluten Free", "Kosher Certified", "Born for the Pit", "11 Bold Blends", "Low & Slow",
                   "Hot & Fast", "Seasoned Like No Other"]
    strip = "".join(f'<span class="strip__item">{escape(w)}</span>' for w in strip_words * 2)
    pit_imgs = {"Beef": "sliced-steak", "Pork": "ribs", "Poultry": "kebabs", "Seafood": "shrimp", "Veggies": "veggies"}
    picker = "".join(
        f'<a href="/products/#{pit}" style="background-image:url(/assets/img/{pit_imgs[pit]}-900.webp)">'
        f'<span class="h3">{pit}</span><small>{sum(pit in pits_for(p) for p in PRODUCTS)} blends →</small></a>'
        for pit in PITS
    )
    temps = [
        ("Brisket", 203, "Probe-tender, rest 1 hr+", "Pit 225–275°F"),
        ("Pork Shoulder", 200, "Bone pulls clean", "Pit 225–250°F"),
        ("Spare Ribs", 198, "Bend test, bark cracks", "Pit 250°F"),
        ("Chicken Thighs", 175, "Renders crisp skin", "Pit 300–350°F"),
        ("Steak, Med-Rare", 130, "Pull at 125°F, rest", "Hot & fast"),
        ("Salmon", 125, "Flakes, still glossy", "Medium direct"),
    ]
    temp_html = "".join(
        f'<div class="temp reveal"><div class="temp__cut">{cut}</div><div class="temp__num">{t}<sup>°F</sup></div>'
        f'<div class="temp__note">{note}</div><span class="temp__pit">{pit}</span></div>'
        for cut, t, note, pit in temps
    )
    body = f"""
<section class="hero">
  <div class="hero__media">
    <video autoplay muted loop playsinline preload="metadata" poster="/assets/img/flame-grill-1800.webp" aria-hidden="true">
      <source src="/assets/video/grill-loop.webm" type="video/webm">
      <source src="/assets/video/grill-loop.mp4" type="video/mp4">
    </video>
  </div>
  <div class="wrap">
    <span class="script hero__script">Seasoned like no other</span>
    <h1 class="display">Bold BBQ Rubs for <span class="ember">Outlaw</span> Pitmasters</h1>
    <p class="lede">Eleven bold blends built for brisket, ribs, wings and everything else that meets fire. Gluten free, kosher certified and absolutely not polite.</p>
    <div class="hero__ctas">
      <a class="btn" href="/products/">Shop the Lineup <span aria-hidden="true">→</span></a>
      <a class="btn btn--ghost" href="/recipes/">Fire Up a Recipe</a>
    </div>
  </div>
</section>
<div class="strip-wrap" aria-hidden="true"><div class="strip"><div class="strip__track">{strip}</div></div></div>

<section class="section">
  <div class="wrap">
    <div class="section__head">
      <div><span class="eyebrow">Fan Favorites</span><h2 class="h2">Pick Your <span class="ember">Poison</span></h2></div>
      <a class="link-arrow" href="/products/">See all 11 blends <span>→</span></a>
    </div>
    <div class="grid grid--products">{"".join(product_card(p) for p in featured)}</div>
  </div>
</section>

<section class="section section--alt">
  <div class="wrap split">
    <div class="split__media reveal">{img("lineup", "The full Outlaw Spices lineup on a dark table", sizes="(max-width: 860px) 100vw, 55vw")}
      <div class="stamp"><div><strong>11</strong>Bold<br>Blends</div></div>
    </div>
    <div class="reveal">
      <span class="eyebrow">Why Outlaw</span>
      <h2 class="h2">Built for the Pit, <span class="ember">Not the Pantry</span></h2>
      <p>We make rubs for people who light charcoal on a Tuesday. Every blend is designed to stand up to smoke, flame and long cooks, and to build the kind of bark that gets photographed before it gets eaten.</p>
      <ul class="checks">
        <li><div><strong>Made for live fire</strong><span>Coarse, bark-building grinds that hold up from 225°F smokes to 700°F sears.</span></div></li>
        <li><div><strong>Gluten free &amp; kosher</strong><span>Every jar carries both marks. Feed the whole crowd without a second thought.</span></div></li>
        <li><div><strong>A blend for every cook</strong><span>From mild &amp; sweet to Nashville fire. Beef, pork, poultry, seafood and veggies all covered.</span></div></li>
      </ul>
      <a class="btn" href="/products/">Find Your Blend</a>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section__head">
      <div><span class="eyebrow">Match Your Meat</span><h2 class="h2">What's on <span class="ember">the Pit?</span></h2></div>
      <p class="lede">Tell us what you're cooking. We'll tell you what to shake on it.</p>
    </div>
    <div class="picker reveal">{picker}</div>
  </div>
</section>

<section class="section section--alt">
  <div class="wrap">
    <div class="section__head">
      <div><span class="eyebrow">The Outlaw Cookbook</span><h2 class="h2">Recipes Worth <span class="ember">the Smoke</span></h2></div>
      <a class="link-arrow" href="/recipes/">All recipes <span>→</span></a>
    </div>
    <div class="grid grid--recipes">{"".join(recipe_card(r) for r in RECIPES[:3])}</div>
  </div>
</section>

<section class="section" id="pit-guide">
  <div class="wrap">
    <div class="section__head">
      <div><span class="eyebrow">Pit Guide</span><h2 class="h2">Low &amp; Slow <span class="ember">Cheat Sheet</span></h2></div>
      <p class="lede">Target internal temps we cook to. Trust your thermometer, then trust your fork.</p>
    </div>
    <div class="temps">{temp_html}</div>
    <p class="muted" style="font-size:.82rem;margin-top:16px">USDA minimum safe temps: beef, pork &amp; fish 145°F with a 3-minute rest; poultry 165°F; ground meats 160°F.</p>
  </div>
</section>

<section class="section section--alt">
  <div class="wrap split split--rev">
    <div class="split__media split__media--wide reveal">{img("flatlay", "Cookout spread with Outlaw Spices jars, sides and burgers", sizes="(max-width: 860px) 100vw, 55vw")}</div>
    <div class="reveal">
      <span class="eyebrow">Grill Like an Outlaw</span>
      <h2 class="h2">Cooking Is a <span class="ember">Declaration</span></h2>
      <p>There's something about cooking over fire. The sizzle, the smoke and the stories that come with it. Whether you're flipping burgers on the patio or babysitting a brisket overnight, grilling brings people together.</p>
      <p>We just make sure it tastes like you meant it.</p>
      <a class="link-arrow" href="/about">Our story <span>→</span></a>
    </div>
  </div>
</section>
"""
    ld = {"@context": "https://schema.org", "@type": "Organization", "name": "Outlaw Spices", "url": SITE_URL,
          "logo": f"{SITE_URL}/assets/img/logo-white.png", "email": "hello@outlawspice.com"}
    return layout(
        title="Outlaw Spices | Bold BBQ Rubs & Seasonings",
        description="Bold BBQ rubs and seasonings for brisket, ribs, wings and steaks. 11 gluten-free, kosher-certified blends built for the pit. Seasoned like no other.",
        body=body, path="/", jsonld=ld, intro=True,
    )


def shop():
    profiles = sorted({x for p in PRODUCTS for x in p["profile"]})
    body = f"""
<section class="page-hero">
  <div class="page-hero__bg">{img("lineup-2", "", eager=True)}</div>
  <div class="wrap">
    <span class="eyebrow">The Lineup</span>
    <h1 class="display">Shop <span class="ember">BBQ Rubs</span></h1>
    <p class="lede">Eleven blends. Every one gluten free and kosher certified. Filter by what's on the pit or how you like your flavor.</p>
  </div>
</section>
<section class="section section--tight" style="padding-top:20px">
  <div class="wrap">
    {chips("#product-grid", [*PITS, *profiles])}
    <div class="grid grid--products" id="product-grid">{"".join(product_card(p) for p in PRODUCTS)}</div>
  </div>
</section>"""
    ld = {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "url": f"{SITE_URL}/products/{p['slug']}", "name": p["name"]}
        for i, p in enumerate(PRODUCTS)]}
    return layout(title="Shop BBQ Rubs & Seasonings",
                  description="Shop all 11 Outlaw Spices BBQ rubs: Roadhouse Rub, Cowboy Coffee, Nashville Hot, Kansas City's Best and more. Gluten free and kosher.",
                  body=body, path="/products/", active="Shop Blends", image="/assets/img/lineup-2-1800.webp", jsonld=ld)


def product_page(p):
    s = p["slug"]
    views = ["Front of jar", "The blend, up close", "Nutrition panel", "Back label"]
    thumbs = "".join(
        f'<button type="button" data-src="/assets/img/products/{s}-{n}.webp"{" aria-current=true" if n == 1 else ""} aria-label="Show {views[n-1].lower()}">'
        f'<img src="/assets/img/products/{s}-{n}.webp" alt="{escape(p["name"])}: {views[n-1].lower()}" loading="lazy" width="200" height="200"></button>'
        for n in range(1, 5)
    )
    pairs = [r for r in RECIPES if r["blend"] == s]
    others = [o for o in PRODUCTS if o["slug"] != s and set(pits_for(o)) & set(pits_for(p))][:4]
    if len(others) < 4:
        others += [o for o in PRODUCTS if o["slug"] != s and o not in others][: 4 - len(others)]
    steps = "".join(f"<li>{escape(x)}</li>" for x in p["how_to"])
    price = f'<p class="pdp__price">{escape(p["price"])}</p>' if p.get("price") else ""
    best = "".join(f'<span class="pill">{escape(b)}</span>' for b in p["best_on"])
    pair_html = ""
    if pairs:
        pair_html = f"""
<section class="section section--alt section--tight">
  <div class="wrap">
    <div class="section__head"><div><span class="eyebrow">Cook With It</span><h2 class="h2">Recipes Using <span class="ember">{escape(short(p))}</span></h2></div></div>
    <div class="grid grid--recipes">{"".join(recipe_card(r) for r in pairs)}</div>
  </div>
</section>"""
    body = f"""
<section class="pdp" style="--accent:{p['accent']}">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a><span>/</span><a href="/products/">Shop</a><span>/</span>{escape(short(p))}</nav>
    <div class="pdp__grid">
      <div class="gallery">
        <div class="gallery__main"><img src="/assets/img/products/{s}-1.webp" alt="{escape(p['name'])} jar" width="900" height="900" fetchpriority="high"></div>
        <div class="gallery__thumbs">{thumbs}</div>
      </div>
      <div>
        <span class="pdp__tagline">{escape(p['tagline'])}</span>
        <h1>{escape(p['name'])}</h1>
        <div class="pdp__weight">Net wt. {escape(p['net_weight'])}</div>
        {price}
        <p class="pdp__desc">{escape(p['description'])}</p>
        <div class="cta-row">
          <a class="btn" href="#posse">Get It First</a>
          <a class="btn btn--ghost" href="/recipes/">Find a Recipe</a>
        </div>
        <dl class="facts">
          <div><dt>Heat</dt><dd>{heat(p['heat'])}</dd></div>
          <div><dt>Flavor</dt><dd>{escape(" · ".join(p['profile']))}</dd></div>
          <div style="grid-column:1/-1"><dt>Best on</dt><dd class="pills">{best}</dd></div>
        </dl>
        <div class="badges"><span><b>GF</b>Gluten free</span><span><b>U</b>Kosher certified</span><span><b>✦</b>Premium quality</span></div>
        <div class="howto">
          <span class="eyebrow">How to Use</span>
          <ol>{steps}</ol>
        </div>
      </div>
    </div>
  </div>
</section>
{pair_html}
<section class="section section--tight">
  <div class="wrap">
    <div class="section__head"><div><span class="eyebrow">Ride Along</span><h2 class="h2">Pairs <span class="ember">Well With</span></h2></div><a class="link-arrow" href="/products/">All blends <span>→</span></a></div>
    <div class="grid grid--products">{"".join(product_card(o) for o in others)}</div>
  </div>
</section>"""
    ld = {"@context": "https://schema.org", "@type": "Product", "name": p["name"], "description": p["description"],
          "image": [f"{SITE_URL}/assets/img/products/{s}-{n}.webp" for n in range(1, 5)],
          "brand": {"@type": "Brand", "name": "Outlaw Spices"}, "url": f"{SITE_URL}/products/{s}"}
    return layout(title=f"{p['name']} — {p['tagline']}",
                  description=f"{p['short']} {p['net_weight']}. Gluten free, kosher certified BBQ seasoning from Outlaw Spices.",
                  body=body, path=f"/products/{s}", active="Shop Blends",
                  image=f"/assets/img/products/{s}-1.webp", jsonld=ld)


def recipes_index():
    cats = sorted({r["category"] for r in RECIPES} | {r["method"] for r in RECIPES})
    body = f"""
<section class="page-hero">
  <div class="page-hero__bg">{img("mixed-grill", "", eager=True)}</div>
  <div class="wrap">
    <span class="eyebrow">The Outlaw Cookbook</span>
    <h1 class="display">Recipes Worth <span class="ember">the Smoke</span></h1>
    <p class="lede">Pit-tested cooks from overnight brisket to ten-minute shrimp. Every one built around an Outlaw blend.</p>
  </div>
</section>
<section class="section section--tight" style="padding-top:20px">
  <div class="wrap">
    {chips("#recipe-grid", cats)}
    <div class="grid grid--recipes" id="recipe-grid">{"".join(recipe_card(r) for r in RECIPES)}</div>
  </div>
</section>"""
    return layout(title="BBQ Recipes", description="Smoked brisket, sticky ribs, coffee-rubbed ribeyes, Nashville hot shrimp and more BBQ recipes from Outlaw Spices.",
                  body=body, path="/recipes/", active="Recipes", image="/assets/img/mixed-grill-1800.webp")


def recipe_page(r):
    b = BY_SLUG[r["blend"]]
    ings = "".join(f'<li><label><input type="checkbox"><span>{escape(i)}</span></label></li>' for i in r["ingredients"])
    steps = "".join(f"<li>{escape(x)}</li>" for x in r["steps"])
    more = [x for x in RECIPES if x["slug"] != r["slug"]][:3]
    body = f"""
<section class="recipe-hero">
  <div class="recipe-hero__bg">{img(r['image'], r['title'], eager=True)}</div>
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a><span>/</span><a href="/recipes/">Recipes</a><span>/</span>{escape(r['title'])}</nav>
    <span class="eyebrow">{escape(r['method'])} · {escape(r['category'])}</span>
    <h1 class="display">{escape(r['title'])}</h1>
    <p class="lede" style="margin-top:16px">{escape(r['summary'])}</p>
    <dl class="recipe-stats">
      <div><dt>Prep</dt><dd>{escape(r['prep'])}</dd></div>
      <div><dt>Cook</dt><dd>{escape(r['cook'])}</dd></div>
      <div><dt>Serves</dt><dd>{r['serves']}</dd></div>
      <div><dt>Level</dt><dd>{escape(r['level'])}</dd></div>
    </dl>
  </div>
</section>
<div class="wrap recipe-body">
  <aside>
    <div class="ingredients">
      <span class="eyebrow">Ingredients</span>
      <ul>{ings}</ul>
    </div>
    <a class="blend-callout" href="/products/{b['slug']}">
      <img src="/assets/img/products/{b['slug']}-1-480.webp" alt="{escape(b['name'])} jar" width="96" height="96" loading="lazy">
      <span><small>The blend</small><b>{escape(b['name'])}</b><br><span class="link-arrow" style="font-size:.75rem">Shop it <span>→</span></span></span>
    </a>
  </aside>
  <div>
    <span class="eyebrow">Method</span>
    <ol class="steps">{steps}</ol>
    <div class="tip"><strong>Pitmaster tip</strong>{escape(r['tip'])}</div>
  </div>
</div>
<section class="section section--alt section--tight">
  <div class="wrap">
    <div class="section__head"><div><span class="eyebrow">Keep Cooking</span><h2 class="h2">More <span class="ember">Recipes</span></h2></div><a class="link-arrow" href="/recipes/">All recipes <span>→</span></a></div>
    <div class="grid grid--recipes">{"".join(recipe_card(x) for x in more)}</div>
  </div>
</section>"""
    ld = {"@context": "https://schema.org", "@type": "Recipe", "name": r["title"], "description": r["summary"],
          "image": f"{SITE_URL}/assets/img/{r['image']}-1800.webp", "recipeYield": f"{r['serves']} servings",
          "recipeCategory": r["category"], "recipeIngredient": r["ingredients"],
          "recipeInstructions": [{"@type": "HowToStep", "text": x} for x in r["steps"]],
          "author": {"@type": "Organization", "name": "Outlaw Spices"}}
    return layout(title=r["title"], description=r["summary"], body=body, path=f"/recipes/{r['slug']}",
                  active="Recipes", image=f"/assets/img/{r['image']}-1800.webp", jsonld=ld)


def about():
    body = f"""
<section class="page-hero">
  <div class="page-hero__bg">{img("grillside", "", eager=True)}</div>
  <div class="wrap">
    <span class="eyebrow">Our Story</span>
    <h1 class="display">Grill Like <span class="ember">an Outlaw</span></h1>
    <p class="lede">Cooking isn't just a necessity. It's a declaration of boldness, creativity and a love for flavor.</p>
  </div>
</section>
<section class="section">
  <div class="wrap split">
    <div class="split__media reveal">{img("cutting-board", "Outlaw Spices jar on a wooden cutting board", sizes="(max-width: 860px) 100vw, 55vw", widths=(900, 1600))}</div>
    <div class="reveal">
      <span class="eyebrow">Why We Exist</span>
      <h2 class="h2">Arming Backyard <span class="ember">Heroes</span></h2>
      <p>Outlaw Spices started with a simple idea: the people who cook over fire deserve seasonings as bold as they are. Our mission is to arm grill enthusiasts, tailgate legends and backyard heroes with the ultimate tools of the trade: blends that turn every cook into something worth talking about.</p>
      <p>There's something special about cooking over fire. The sizzle, the smoke and the stories that come with it. Whether you're flipping burgers on the patio or smoking ribs out in the wild, grilling brings people together. We just make sure it tastes like you meant it.</p>
      <p>So grab a jar, fire up the grill, and let's cook something unforgettable.</p>
    </div>
  </div>
</section>
<section class="section section--alt">
  <div class="wrap">
    <div class="section__head"><div><span class="eyebrow">The Outlaw Code</span><h2 class="h2">What We <span class="ember">Ride For</span></h2></div></div>
    <div class="values">
      <div class="value reveal"><div class="num">01</div><h3 class="h3">Flavor First</h3><p>Every blend has to earn its place on the grate. If it doesn't make you go back for seconds, it doesn't ship.</p></div>
      <div class="value reveal"><div class="num">02</div><h3 class="h3">Built for Fire</h3><p>Grinds and balances designed for smoke, flame and long cooks. Not for sitting in a cabinet.</p></div>
      <div class="value reveal"><div class="num">03</div><h3 class="h3">Feed Everybody</h3><p>Gluten free and kosher certified across the line, so nobody at the table gets left out.</p></div>
      <div class="value reveal"><div class="num">04</div><h3 class="h3">No Rules</h3><p>Coffee on brisket. Honey mustard on salmon. Nashville hot on everything. Outlaws cook how they want.</p></div>
    </div>
  </div>
</section>
<section class="section">
  <div class="wrap split split--rev">
    <div class="split__media split__media--wide reveal">{img("lineup", "The Outlaw Spices lineup", sizes="(max-width: 860px) 100vw, 55vw")}</div>
    <div class="reveal">
      <span class="eyebrow">The Lineup</span>
      <h2 class="h2">Eleven Ways to <span class="ember">Break the Rules</span></h2>
      <p>From the everyday crust of Roadhouse Rub to the full-on burn of Nashville Hot, there's an Outlaw for every cut and every cook.</p>
      <a class="btn" href="/products/">Shop All Blends</a>
    </div>
  </div>
</section>"""
    return layout(title="Our Story", description="Outlaw Spices makes bold BBQ rubs for people who cook over fire. Gluten free, kosher certified, seasoned like no other.",
                  body=body, path="/about", active="Our Story", image="/assets/img/grillside-1800.webp")


def not_found():
    body = """
<section class="notfound">
  <div>
    <span class="script" style="font-size:2.2rem">Well, shoot.</span>
    <h1 class="display">404</h1>
    <p class="lede" style="margin:10px auto 30px">This trail's gone cold. The page you're after wandered off the ranch.</p>
    <div class="hero__ctas" style="justify-content:center"><a class="btn" href="/">Head Home</a><a class="btn btn--ghost" href="/products/">Shop Blends</a></div>
  </div>
</section>"""
    return layout(title="Page Not Found", description="This page wandered off the ranch.", body=body, path="/404")


def sitemap():
    paths = ["/", "/products/", "/recipes/", "/about"]
    paths += [f"/products/{p['slug']}" for p in PRODUCTS] + [f"/recipes/{r['slug']}" for r in RECIPES]
    urls = "".join(f"<url><loc>{SITE_URL}{p}</loc></url>" for p in paths)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n'


def write(rel, text):
    path = OUT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main():
    write("index.html", home())
    write("products/index.html", shop())
    for p in PRODUCTS:
        write(f"products/{p['slug']}.html", product_page(p))
    write("recipes/index.html", recipes_index())
    for r in RECIPES:
        write(f"recipes/{r['slug']}.html", recipe_page(r))
    write("about.html", about())
    write("404.html", not_found())
    write("sitemap.xml", sitemap())
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    print(f"built {len(PRODUCTS)} products, {len(RECIPES)} recipes -> {OUT}")


if __name__ == "__main__":
    main()
