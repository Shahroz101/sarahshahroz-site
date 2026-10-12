#!/usr/bin/env python3
import sys
import os
import json
import glob
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_article import ArticleParser
import re

SRC_DIR = "/Users/shahrozburhan/Desktop/Khizra Shahroz Articles HTML"
OUT_PATH = sys.argv[1] if len(sys.argv) > 1 else "all_articles.jsonl"


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


files = sorted(glob.glob(os.path.join(SRC_DIR, "*.html")))
errors = []
with open(OUT_PATH, "w", encoding="utf-8") as out:
    for path in files:
        slug = re.sub(r"\.html$", "", os.path.basename(path))
        try:
            with open(path, "r", encoding="utf-8") as f:
                html = f.read()
            p = ArticleParser()
            p.feed(html)
            blocks = [
                b for b in p.blocks
                if not (b["type"] == "p" and b["text"].strip().startswith("Back to all posts"))
            ]
            word_count = block_word_count(blocks)
            img_count = sum(1 for b in blocks if b["type"] == "img")
            rec = {
                "slug": slug,
                "title": p.title,
                "dek": p.dek,
                "category": p.category,
                "word_count": word_count,
                "img_count": img_count,
                "block_count": len(blocks),
                "blocks": blocks,
            }
            out.write(json.dumps(rec) + "\n")
        except Exception as e:
            errors.append((slug, str(e), traceback.format_exc()))

print(f"Processed {len(files)} files, {len(errors)} errors")
for slug, msg, tb in errors:
    print("ERROR:", slug, msg)
