#!/usr/bin/env python3
"""Check which source files have <h3>, <ul>, or <blockquote> INSIDE the article body
(not nav/footer), since the current extractor silently drops these."""
import os
import glob
import re
from html.parser import HTMLParser

SRC_DIR = "/Users/shahrozburhan/Desktop/Khizra Shahroz Articles HTML"


class BodyTagChecker(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_article = False
        self.depth = 0
        self.found = set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get("class", "")
        if tag == "article" and "prose" in cls:
            self.in_article = True
            self.depth = 0
            return
        if self.in_article:
            self.depth += 1
            if tag in ("h3", "ul", "blockquote", "ol", "h4"):
                self.found.add(tag)

    def handle_endtag(self, tag):
        if tag == "article" and self.in_article:
            self.in_article = False
            return
        if self.in_article:
            self.depth -= 1


def main():
    files = sorted(glob.glob(os.path.join(SRC_DIR, "*.html")))
    affected = []
    for path in files:
        slug = re.sub(r"\.html$", "", os.path.basename(path))
        with open(path, encoding="utf-8") as f:
            html = f.read()
        checker = BodyTagChecker()
        checker.feed(html)
        if checker.found:
            affected.append((slug, sorted(checker.found)))

    print(f"Total files: {len(files)}")
    print(f"Files with h3/ul/blockquote/ol/h4 INSIDE article body: {len(affected)}")
    for slug, tags in affected:
        print(f"  {slug}: {tags}")


if __name__ == "__main__":
    main()
