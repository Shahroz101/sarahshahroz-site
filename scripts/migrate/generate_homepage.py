#!/usr/bin/env python3
"""Rebuild the site homepage (index.html) from progress.json real article data."""
import os
import json
import html

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

TOP_CATEGORIES = ["Decorating", "Bathroom", "Living Room", "Bedroom", "Kitchen", "Outdoor"]


def esc(text):
    return html.escape(text, quote=False)


def main():
    with open(os.path.join(HERE, "progress.json"), encoding="utf-8") as f:
        progress = json.load(f)

    items = [v for v in progress.values() if v.get("status") == "done"]
    items.sort(key=lambda v: v["date"], reverse=True)

    featured = items[0]
    latest = items[1:5]

    featured_html = f"""        <a href="{featured['new_slug']}" class="featured-post">
          <div class="featured-image" aria-hidden="true"><img src="{featured['hero_image']}" alt="" loading="lazy"></div>
          <div class="featured-content">
            <span class="tag">{esc(featured['category'])}</span>
            <h2>{esc(featured['title'])}</h2>
            <p>{esc(featured['dek'])}</p>
            <span class="meta">{featured['date']} &middot; {featured['minutes']} min read</span>
          </div>
        </a>"""

    cards = []
    for it in latest:
        cards.append(f"""          <article class="post-card">
            <a href="{it['new_slug']}"><div class="post-image" aria-hidden="true"><img src="{it['hero_image']}" alt="" loading="lazy"></div></a>
            <div class="post-body">
              <span class="tag">{esc(it['category'])}</span>
              <h3><a href="{it['new_slug']}">{esc(it['title'])}</a></h3>
              <p>{esc(it['dek'])}</p>
              <span class="meta">{it['date']}</span>
            </div>
          </article>""")
    cards_html = "\n\n".join(cards)

    pills_html = "\n          ".join(
        f'<a href="articles/index.html" class="pill">{esc(c)}</a>' for c in TOP_CATEGORIES
    )

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Sarah Shahroz | A Home Decor Blog</title>
  <link rel="stylesheet" href="css/style.css?v=2">
</head>
<body>

  <header class="site-header">
    <div class="container header-inner">
      <a href="index.html" class="logo">Sarah&nbsp;Shahroz</a>

      <nav class="main-nav" id="main-nav">
        <a href="#latest">Latest</a>
        <a href="articles/index.html">All Articles</a>
        <a href="#categories">Categories</a>
        <a href="#about">About</a>
        <a href="#newsletter">Newsletter</a>
      </nav>

      <button class="nav-toggle" id="nav-toggle" aria-label="Toggle menu">
        <span></span><span></span><span></span>
      </button>
    </div>
  </header>

  <main>
    <section class="hero">
      <div class="container hero-inner">
        <p class="eyebrow">A Home Decor Journal</p>
        <h1>Ideas, stories, and styling tips for a home you love.</h1>
        <p class="hero-sub">Real-life room makeovers, seasonal decorating guides, and small-space solutions &mdash; written for people who love their home, not just Pinterest boards.</p>
        <a href="#latest" class="btn btn-primary">Read the Blog</a>
      </div>
    </section>

    <section class="featured">
      <div class="container">
{featured_html}
      </div>
    </section>

    <section class="latest" id="latest">
      <div class="container">
        <h2>Latest Posts</h2>
        <div class="post-grid">

{cards_html}

        </div>
      </div>
    </section>

    <section class="categories" id="categories">
      <div class="container">
        <h2>Browse by Topic</h2>
        <div class="category-pills">
          {pills_html}
        </div>
      </div>
    </section>

    <section class="story" id="about">
      <div class="container story-inner">
        <div class="story-text">
          <h2>Hi, I'm glad you're here.</h2>
          <p>
            I'm Sarah &mdash; I started writing about home decor because I was
            tired of advice that only worked in a show home. Everything here
            comes from rooms I've actually lived in, redone on an actual
            budget, with the mistakes left in.
          </p>
          <p>
            No affiliate-stuffed "must haves," no sponsored clutter &mdash;
            just styling ideas, small fixes, and seasonal guides for a home
            that fits how you really live in it.
          </p>
          <a href="articles/index.html" class="btn btn-secondary">Read the Latest Posts</a>
        </div>
        <div class="story-image" aria-hidden="true"></div>
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
"""

    out_path = os.path.join(ROOT, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"Homepage rebuilt: featured={featured['new_slug']}, latest={len(latest)} -> {out_path}")


if __name__ == "__main__":
    main()
