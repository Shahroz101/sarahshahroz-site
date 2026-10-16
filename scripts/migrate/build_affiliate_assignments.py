#!/usr/bin/env python3
"""Build per-article, per-image product assignments from the Affiliate Links export.

For every Sarah Shahroz article, matches each inline image (by its alt text,
which was preserved verbatim from the Khizra Shahroz source) to the product
pair Khizra displayed under that same photo. Images with no exact caption
match fall back to a same-article product pair, cycling through the
article's own pairs so every image gets 1-2 relevant products.

Writes scripts/migrate/affiliate_assignments.json:
  { new_slug: [ [product, ...], ... ] }   # one list of 1-2 products per image, in image order
Each product: {asin, title, affiliate_link, src_path, width, height}
src_path is relative to the Affiliate Links folder root.
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
AFFILIATE_ROOT = os.path.expanduser("~/Desktop/Affiliate Links")
MASTER_CSV = os.path.join(AFFILIATE_ROOT, "00 - ALL LINKS (master list).csv")


def load_groups_by_url():
    groups_by_url = {}
    with open(MASTER_CSV, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            url = row["Article URL"]
            key = (row["Section"], row["Photo it sits under"])
            groups = groups_by_url.setdefault(url, [])
            if not groups or groups[-1]["key"] != key:
                groups.append({"key": key, "products": []})
            groups[-1]["products"].append(row)
    return groups_by_url


def product_from_row(row):
    return {
        "asin": row["ASIN"],
        "title": row["Product title"],
        "affiliate_link": row["Affiliate link"],
        "src_path": row["Image file (from this folder)"],
        "width": row["Image width (px)"],
        "height": row["Image height (px)"],
    }


def main():
    with open(os.path.join(HERE, "progress.json"), encoding="utf-8") as f:
        progress = json.load(f)

    groups_by_url = load_groups_by_url()

    assignments = {}
    stats = {"own_alt_match": 0, "own_positional_fallback": 0, "images": 0}

    for old_slug, info in progress.items():
        new_slug = info["new_slug"]
        khizra_url = f"https://khizrashahroz.com/{old_slug}/"
        own_groups = groups_by_url.get(khizra_url)
        if not own_groups:
            raise RuntimeError(f"no affiliate data for {old_slug}")

        own_caps = {}
        for g in own_groups:
            cap = g["key"][1].strip().lower()
            own_caps.setdefault(cap, g)

        draft_path = os.path.join(HERE, "drafts", f"{new_slug}.json")
        with open(draft_path, encoding="utf-8") as f:
            draft = json.load(f)

        img_blocks = [b for b in draft["blocks"] if b["type"] == "img"]
        per_image = []
        for i, b in enumerate(img_blocks):
            stats["images"] += 1
            alt = b["alt"].strip().lower()
            group = own_caps.get(alt)
            if group is not None:
                stats["own_alt_match"] += 1
            else:
                group = own_groups[i % len(own_groups)]
                stats["own_positional_fallback"] += 1
            products = [product_from_row(r) for r in group["products"][:2]]
            per_image.append(products)

        assignments[new_slug] = per_image

    out_path = os.path.join(HERE, "affiliate_assignments.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(assignments, f, indent=2)

    print(f"Wrote {out_path}")
    print(stats)


if __name__ == "__main__":
    main()
