#!/usr/bin/env python3
"""Pretty-print one extracted article's blocks for reading/rewriting.
Usage: python3 get_article.py <old-slug>
"""
import sys
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

def main():
    slug = sys.argv[1]
    with open(os.path.join(HERE, "all_articles.jsonl"), encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            if d["slug"] == slug:
                print(f"SLUG: {d['slug']}")
                print(f"TITLE: {d['title']}")
                print(f"DEK: {d['dek']}")
                print(f"CATEGORY: {d['category']}")
                print(f"WORD COUNT: {d['word_count']}")
                print(f"IMAGE COUNT: {d['img_count']}")
                print("---BLOCKS---")
                img_n = 0
                for b in d["blocks"]:
                    if b["type"] == "h2":
                        print(f"\n## {b['text']}")
                    elif b["type"] == "h3":
                        print(f"\n### {b['text']}")
                    elif b["type"] == "p":
                        print(f"- {b['text']}")
                    elif b["type"] == "list":
                        marker = "1." if b.get("ordered") else "*"
                        for item in b["items"]:
                            print(f"  {marker} {item}")
                    elif b["type"] == "quote":
                        print(f"  > {b['text']}" + (f" (— {b['cite']})" if b.get("cite") else ""))
                    elif b["type"] == "img":
                        img_n += 1
                        credit = f" [credit: {b['credit_name']} -> {b['credit_url']}]" if b.get("credit_name") else ""
                        print(f"\n[IMG {img_n}] {b['src']} (alt: {b['alt']}){credit}")
                return
    print(f"NOT FOUND: {slug}", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    main()
