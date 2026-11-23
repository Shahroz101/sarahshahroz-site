"""Builds an article page in the lesson-first house style.

usage: build_v2.py <slug> <content_module> <parsed_json> <name_map_json>
content module defines: TITLE, DEK, HERO_IDEA, HERO_ALT, MINUTES, INTRO, RULES_HEADING,
RULES, GROUPS, MISTAKES_HEADING, MISTAKES, CLOSING and optionally RECIPES, PHOTO_OF,
PRODUCTS_OF, CATEGORY, DATE.
"""
import json, html, os, sys, importlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = "/Users/shahrozburhan/Desktop/Websites/Sarah Shahroz"

SLUG, MOD, PARSED, NAMEMAP = sys.argv[1:5]
C = importlib.import_module(MOD)

parsed = json.load(open(os.path.join(HERE, PARSED)))
name_map = json.load(open(os.path.join(HERE, NAMEMAP)))
ideas_by_num = {i + 1: it for i, it in enumerate([x for x in parsed if x.get("image")])}
N = len(ideas_by_num)
RECIPES = getattr(C, "RECIPES", {})
PHOTO_OF = getattr(C, "PHOTO_OF", {})
PRODUCTS_OF = getattr(C, "PRODUCTS_OF", {})
CATEGORY = getattr(C, "CATEGORY", "Entertaining")
DATE = getattr(C, "DATE", "2026-10-31")

def esc(t):
    return html.escape(t, quote=False)

def para(s):
    return f"<p>{esc(s)}</p>"

all_ideas = [idea for _, ideas in C.GROUPS for idea in ideas]
assert len(all_ideas) == N, (len(all_ideas), N)
assert {i[0] for i in all_ideas} == set(range(1, N + 1))
if RECIPES:
    assert set(RECIPES) == set(range(1, N + 1))

sections = []
pos = 0
for group_title, ideas in C.GROUPS:
    sections.append(f"<h2>{esc(group_title)}</h2>")
    for orig_num, title, paragraphs, label in ideas:
        pos += 1
        photo_num = PHOTO_OF.get(orig_num, orig_num)
        pin = ideas_by_num[photo_num]["pin"]
        fname = name_map[str(photo_num)]
        img_path = f"images/articles/{SLUG}/{fname}.jpg"
        assert os.path.exists(os.path.join(ROOT, img_path)), img_path
        prods = []
        for asin_file, p_alt in ideas_by_num[PRODUCTS_OF.get(orig_num, orig_num)]["products"]:
            asin = asin_file.replace(".jpg", "")
            prods.append(f'''      <div class="product-card">
        <img class="product-photo" src="images/articles/{SLUG}/products/{asin_file}" alt="{esc(p_alt)}" loading="lazy">
        <p class="product-title">{esc(p_alt)}</p>
        <a class="shop-cta" href="https://www.amazon.com/dp/{asin}?tag=dwellingdre0c-20" target="_blank" rel="nofollow sponsored noopener">Shop on Amazon</a>
      </div>''')
        recipe = ""
        if RECIPES:
            recipe = f'\n\n<p class="recipe-cta-wrap"><a class="recipe-cta" href="{RECIPES[orig_num]}" target="_blank" rel="noopener">View Recipe</a></p>'
        body = "\n\n".join(para(p) for p in paragraphs)
        grid = ('<div class="product-grid">\n' + chr(10).join(prods) + '\n    </div>') if prods else ""
        sections.append(f'''<h3>{pos}. {esc(title)}</h3>

{body}

<figure>
      <img src="{img_path}" alt="{esc(label)}" loading="lazy">
      <figcaption class="photo-credit"><a href="https://www.pinterest.com/pin/{pin}/" target="_blank" rel="nofollow noopener">Photo via Pinterest &mdash; {esc(label)}</a></figcaption>
    </figure>{recipe}

{grid}''')

rules_html = "<ul>\n" + "\n".join(f"  <li><strong>{esc(r)}</strong> {esc(x)}</li>" for r, x in C.RULES) + "\n</ul>"
mistakes_html = "<ul>\n" + "\n".join(f"  <li><strong>{esc(m)}</strong> {esc(f)}</li>" for m, f in C.MISTAKES) + "\n</ul>"
hero_pin = ideas_by_num[C.HERO_IDEA]["pin"]

page = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <script async src="https://www.googletagmanager.com/gtm.js?id=GTM-KGNP77F4"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
  </script>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(C.TITLE)} | Sarah Shahroz</title>
  <link rel="stylesheet" href="css/style.css?v=3">
</head>
<body>

  <header class="site-header">
    <div class="container header-inner">
      <a href="index.html" class="logo">Sarah&nbsp;Shahroz</a>

      <nav class="main-nav" id="main-nav">
        <a href="index.html#latest">Latest</a>
        <a href="articles/index.html">All Articles</a>
        <a href="index.html#categories">Categories</a>
        <a href="index.html#about">About</a>
        <a href="index.html#newsletter">Newsletter</a>
      </nav>

      <button class="nav-toggle" id="nav-toggle" aria-label="Toggle menu">
        <span></span><span></span><span></span>
      </button>
    </div>
  </header>

  <main>
    <section class="post-hero">
      <div class="container">
        <p class="breadcrumb"><a href="articles/index.html">Articles</a> / {esc(CATEGORY)}</p>
        <h1>{esc(C.TITLE)}</h1>
        <p class="post-dek">{C.DEK}</p>
        <p class="post-meta">{DATE} &middot; {C.MINUTES} min read</p>
      </div>
    </section>

    <section class="article-section">
      <div class="container article-content">

{chr(10).join(para(p) + chr(10) for p in C.INTRO)}
<figure>
      <img src="images/articles/{SLUG}/hero.jpg" alt="{esc(C.HERO_ALT)}" loading="lazy">
      <figcaption class="photo-credit"><a href="https://www.pinterest.com/pin/{hero_pin}/" target="_blank" rel="nofollow noopener">Photo via Pinterest &mdash; {esc(C.HERO_ALT)}</a></figcaption>
    </figure>

<h2>{esc(C.RULES_HEADING)}</h2>

{rules_html}

{chr(10).join(sections)}

<h2>{esc(C.MISTAKES_HEADING)}</h2>

{mistakes_html}

<h2>Where to Start</h2>

{chr(10).join(para(p) + chr(10) for p in C.CLOSING)}
        <p class="post-back"><a href="articles/index.html">&larr; Back to all articles</a></p>
      </div>
    </section>

    <section class="newsletter" id="newsletter">
      <div class="container newsletter-inner">
        <h2>Get new posts in your inbox</h2>
        <p>One email a week. No spam, no sponsored clutter &mdash; just the latest stories.</p>
        <form class="newsletter-form">
          <input type="email" placeholder="Your email address" aria-label="Email address" required>
          <button type="submit" class="btn btn-primary">Subscribe</button>
        </form>
      </div>
    </section>
  </main>

  <footer class="site-footer">
    <div class="container footer-inner">
      <p>&copy; 2026 Sarah Shahroz. All rights reserved.</p>
      <div class="footer-links">
        <a href="#">Instagram</a>
        <a href="#">Pinterest</a>
        <a href="#">Contact</a>
      </div>
    </div>
  </footer>

  <script src="js/script.js"></script>
</body>
</html>
'''

out = os.path.join(ROOT, f"{SLUG}.html")
open(out, "w", encoding="utf-8").write(page)
print("written:", out, "length:", len(page), "ideas:", pos)
