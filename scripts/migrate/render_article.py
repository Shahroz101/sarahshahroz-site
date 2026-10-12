#!/usr/bin/env python3
"""Render a rewritten article draft into a Sarah Shahroz article page.

Usage: python3 render_article.py <draft.json>

Draft JSON shape:
{
  "old_slug": "choosing-living-room-curtains",
  "new_slug": "living-room-curtain-buying-guide",
  "category": "Living Room",
  "title": "...",
  "dek": "...",
  "date": "2026-10-11",
  "blocks": [
    {"type": "p", "text": "..."},
    {"type": "h2", "text": "..."},
    {"type": "img", "src": "https://khizrashahroz.com/images/.../hero.jpg",
     "filename": "hero.jpg", "alt": "...",
     "credit_name": "Photo by X via Unsplash" | null,
     "credit_url": "https://unsplash.com/..." | null}
  ]
}

Downloads each img's src into images/articles/<new_slug>/<filename>,
writes articles/<new_slug>.html, updates progress.json, and rebuilds
articles/index.html.
"""
import sys
import os
import json
import math
import html
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))  # New website/

sys.path.insert(0, HERE)
from common import HEADER, FOOTER, NEWSLETTER_SECTION  # noqa: E402

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"


def esc(text):
    return html.escape(text, quote=False)


def download_image(url, dest_path):
    if os.path.exists(dest_path):
        return
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = resp.read()
    with open(dest_path, "wb") as f:
        f.write(data)


def render_blocks(blocks, new_slug):
    out = []
    img_dir_rel = f"../images/articles/{new_slug}"
    for b in blocks:
        if b["type"] == "p":
            out.append(f"<p>{esc(b['text'])}</p>")
        elif b["type"] == "h2":
            out.append(f"<h2>{esc(b['text'])}</h2>")
        elif b["type"] == "h3":
            out.append(f"<h3>{esc(b['text'])}</h3>")
        elif b["type"] == "list":
            tag = "ol" if b.get("ordered") else "ul"
            items = "\n".join(f"      <li>{esc(item)}</li>" for item in b["items"])
            out.append(f"<{tag}>\n{items}\n    </{tag}>")
        elif b["type"] == "quote":
            cite_html = f"\n      <cite>{esc(b['cite'])}</cite>" if b.get("cite") else ""
            out.append(f'<blockquote>\n      <p>{esc(b["text"])}</p>{cite_html}\n    </blockquote>')
        elif b["type"] == "img":
            local_path = f"{img_dir_rel}/{b['filename']}"
            dest_fs = os.path.join(ROOT, "images", "articles", new_slug, b["filename"])
            download_image(b["src"], dest_fs)
            credit_html = ""
            if b.get("credit_name"):
                if b.get("credit_url"):
                    credit_html = (
                        f'<figcaption class="photo-credit">'
                        f'<a href="{esc(b["credit_url"])}" target="_blank" rel="nofollow noopener">'
                        f'{esc(b["credit_name"])}</a></figcaption>'
                    )
                else:
                    credit_html = f'<figcaption class="photo-credit">{esc(b["credit_name"])}</figcaption>'
            out.append(
                f'<figure>\n      <img src="{local_path}" alt="{esc(b["alt"])}" loading="lazy">\n'
                f'      {credit_html}\n    </figure>'
            )
    return "\n\n".join(out)


def block_word_count(blocks):
    total = 0
    for b in blocks:
        if b["type"] in ("p", "h2", "h3"):
            total += len(b["text"].split())
        elif b["type"] == "list":
            for item in b["items"]:
                total += len(item.split())
        elif b["type"] == "quote":
            total += len(b["text"].split())
            if b.get("cite"):
                total += len(b["cite"].split())
    return total


def read_minutes(blocks):
    return max(1, round(block_word_count(blocks) / 200))


def original_stats(old_slug):
    path = os.path.join(HERE, "all_articles.jsonl")
    with open(path, encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            if rec["slug"] == old_slug:
                return rec["word_count"], rec["img_count"]
    return None, None


def main():
    draft_path = sys.argv[1]
    with open(draft_path, encoding="utf-8") as f:
        d = json.load(f)

    new_slug = d["new_slug"]
    minutes = read_minutes(d["blocks"])
    body_html = render_blocks(d["blocks"], new_slug)

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(d['title'])} | Sarah Shahroz</title>
  <link rel="stylesheet" href="../css/style.css">
</head>
<body>

  {HEADER.strip()}

  <main>
    <section class="post-hero">
      <div class="container">
        <p class="breadcrumb"><a href="index.html">Articles</a> / {esc(d['category'])}</p>
        <h1>{esc(d['title'])}</h1>
        <p class="post-dek">{esc(d['dek'])}</p>
        <p class="post-meta">{d['date']} &middot; {minutes} min read</p>
      </div>
    </section>

    <section class="article-section">
      <div class="container article-content">

{body_html}

        <p class="post-back"><a href="index.html">&larr; Back to all articles</a></p>
      </div>
    </section>

    {NEWSLETTER_SECTION.strip()}
  </main>

  {FOOTER.strip()}
</body>
</html>
"""

    out_path = os.path.join(ROOT, "articles", f"{new_slug}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page)

    # update progress.json
    progress_path = os.path.join(HERE, "progress.json")
    with open(progress_path, encoding="utf-8") as f:
        progress = json.load(f)

    hero = next((b for b in d["blocks"] if b["type"] == "img"), None)
    word_count = block_word_count(d["blocks"])

    progress[d["old_slug"]] = {
        "new_slug": new_slug,
        "title": d["title"],
        "dek": d["dek"],
        "category": d["category"],
        "date": d["date"],
        "minutes": minutes,
        "word_count": word_count,
        "hero_image": f"images/articles/{new_slug}/{hero['filename']}" if hero else None,
        "status": "done",
    }

    with open(progress_path, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2)

    orig_wc, orig_imgs = original_stats(d["old_slug"])
    new_imgs = sum(1 for b in d["blocks"] if b["type"] == "img")

    print(f"OK: {out_path}")
    print(f"TITLE: {d['title']}")
    print(f"WORDS: {word_count} (source: {orig_wc})  IMAGES: {new_imgs} (source: {orig_imgs})")
    if orig_wc is not None and word_count < orig_wc:
        print(f"WARNING: new article is {orig_wc - word_count} words SHORTER than the source. Add more before shipping.")
    if orig_imgs is not None and new_imgs != orig_imgs:
        print(f"WARNING: image count {new_imgs} does not match source ({orig_imgs}). Check for a dropped or duplicated image.")


if __name__ == "__main__":
    main()
