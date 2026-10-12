#!/usr/bin/env python3
"""Rebuild articles/index.html from progress.json."""
import os
import json
import html
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

sys.path.insert(0, HERE)
from common import HEADER, FOOTER, NEWSLETTER_SECTION  # noqa: E402


def esc(text):
    return html.escape(text, quote=False)


def main():
    with open(os.path.join(HERE, "progress.json"), encoding="utf-8") as f:
        progress = json.load(f)

    items = [v for v in progress.values() if v.get("status") == "done"]
    items.sort(key=lambda v: v["date"], reverse=True)

    cards = []
    for it in items:
        img = f'../{it["hero_image"]}' if it.get("hero_image") else ""
        cards.append(f"""          <article class="post-card">
            <a href="{it['new_slug']}.html"><div class="post-image"><img src="{img}" alt="" loading="lazy"></div></a>
            <div class="post-body">
              <span class="tag">{esc(it['category'])}</span>
              <h3><a href="{it['new_slug']}.html">{esc(it['title'])}</a></h3>
              <p>{esc(it['dek'])}</p>
              <span class="meta">{it['date']} &middot; {it['minutes']} min read</span>
            </div>
          </article>""")

    grid_html = "\n".join(cards) if cards else "<p>New articles are on their way.</p>"

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>All Articles | Sarah Shahroz</title>
  <link rel="stylesheet" href="../css/style.css">
</head>
<body>

  {HEADER.strip()}

  <main>
    <section class="archive-hero">
      <div class="container">
        <h1>All Articles</h1>
        <p>{len(items)} stories on styling, small fixes, and living well at home.</p>
      </div>
    </section>

    <section class="archive-grid">
      <div class="container">
        <div class="post-grid">
{grid_html}
        </div>
      </div>
    </section>

    {NEWSLETTER_SECTION.strip()}
  </main>

  {FOOTER.strip()}
</body>
</html>
"""

    out_path = os.path.join(ROOT, "articles", "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"Archive rebuilt: {len(items)} articles -> {out_path}")


if __name__ == "__main__":
    main()
