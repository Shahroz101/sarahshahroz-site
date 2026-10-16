#!/usr/bin/env python3
"""Copy + resize the product images referenced in affiliate_assignments.json
into each article's images/articles/<new_slug>/products/<asin>.jpg.
Idempotent: skips a destination that already exists.
"""
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
AFFILIATE_ROOT = os.path.expanduser("~/Desktop/Affiliate Links")

MAX_DIM = "480"
QUALITY = "65"


def main():
    with open(os.path.join(HERE, "affiliate_assignments.json"), encoding="utf-8") as f:
        assignments = json.load(f)

    copied = 0
    skipped = 0
    failed = []

    for slug, per_image in assignments.items():
        dest_dir = os.path.join(ROOT, "images", "articles", slug, "products")
        os.makedirs(dest_dir, exist_ok=True)
        seen = set()
        for products in per_image:
            for p in products:
                asin = p["asin"]
                if asin in seen:
                    continue
                seen.add(asin)
                dest = os.path.join(dest_dir, f"{asin}.jpg")
                if os.path.exists(dest):
                    skipped += 1
                    continue
                src = os.path.join(AFFILIATE_ROOT, p["src_path"])
                r = subprocess.run(
                    ["sips", "-Z", MAX_DIM, "-s", "formatOptions", QUALITY, src, "--out", dest],
                    capture_output=True, text=True,
                )
                if r.returncode != 0:
                    failed.append((slug, asin, r.stderr.strip()))
                else:
                    copied += 1

    print(f"copied={copied} skipped={skipped} failed={len(failed)}")
    for f_ in failed[:20]:
        print("FAILED:", f_)


if __name__ == "__main__":
    main()
