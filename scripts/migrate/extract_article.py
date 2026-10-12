#!/usr/bin/env python3
"""Extract structured content from a Khizra Shahroz source article HTML file.

Usage: python3 extract_article.py <file.html>
Prints JSON to stdout: { slug, title, dek, category, blocks: [...] }

blocks is an ordered list of:
  {"type": "p", "text": "..."}
  {"type": "h2", "text": "..."}
  {"type": "img", "src": "https://khizrashahroz.com/images/...", "alt": "...",
   "credit_name": "..." or null, "credit_url": "..." or null}

Product/shop-cta blocks (Amazon affiliate cards) are skipped entirely.
"""
import sys
import json
import re
from html.parser import HTMLParser

SITE = "https://khizrashahroz.com"


class ArticleParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = None
        self.dek = None
        self.category = None
        self.blocks = []

        self._in_head = False
        self._in_title = False
        self._title_buf = ""

        self._in_hero = False
        self._in_breadcrumb = False
        self._breadcrumb_buf = ""
        self._in_h1 = False
        self._h1_buf = ""
        self._in_lede = False
        self._lede_buf = ""

        self._in_article = False
        self._depth_stack = []  # track tag nesting with class context

        self._in_idea_heading = False
        self._in_numeral = False
        self._skipping = False
        self._skip_div_depth = 0  # counts only <div> open/close within the skipped region

        self._in_p = False
        self._p_buf = ""
        self._in_h2 = False
        self._h2_buf = ""

        self._in_figure = False
        self._pending_img = None
        self._in_figcaption = False
        self._figcaption_buf = ""
        self._in_credit_a = False
        self._credit_a_buf = ""
        self._credit_href = None

        self._in_h3 = False
        self._h3_buf = ""

        self._in_list = False
        self._list_ordered = False
        self._list_items = []
        self._in_li = False
        self._li_buf = ""

        self._in_blockquote = False
        self._in_quote_p = False
        self._quote_buf = ""
        self._in_cite = False
        self._cite_buf = ""

        self._article_depth = 0

    def _attrs_dict(self, attrs):
        return {k: v for k, v in attrs}

    def handle_starttag(self, tag, attrs):
        a = self._attrs_dict(attrs)
        cls = a.get("class", "")

        if tag == "head":
            self._in_head = True
        if self._in_head and tag == "title":
            self._in_title = True
            self._title_buf = ""

        if tag == "section" and "page-hero" in cls:
            self._in_hero = True
        if self._in_hero and tag == "p" and "breadcrumb" in cls:
            self._in_breadcrumb = True
            self._breadcrumb_buf = ""
        if self._in_hero and tag == "h1":
            self._in_h1 = True
            self._h1_buf = ""
        if self._in_hero and tag == "p" and "lede" in cls:
            self._in_lede = True
            self._lede_buf = ""

        if tag == "article" and "prose" in cls:
            self._in_article = True
            self._article_depth = 0
            return

        if not self._in_article:
            return

        self._article_depth += 1

        if self._skipping:
            if tag == "div":
                self._skip_div_depth += 1
            return

        # skip affiliate product grids entirely
        if tag == "div" and "product-grid" in cls:
            self._skipping = True
            self._skip_div_depth = 1
            return

        if tag == "div" and "idea-heading" in cls:
            self._in_idea_heading = True
            return

        if self._in_idea_heading and tag == "h2":
            self._in_h2 = True
            self._h2_buf = ""
            return

        if tag == "h2" and not self._in_idea_heading:
            self._in_h2 = True
            self._h2_buf = ""
            return

        if tag == "h3":
            self._in_h3 = True
            self._h3_buf = ""
            return

        if tag in ("ul", "ol") and not self._in_list:
            self._in_list = True
            self._list_ordered = (tag == "ol")
            self._list_items = []
            return

        if tag == "li" and self._in_list:
            self._in_li = True
            self._li_buf = ""
            return

        if tag == "blockquote":
            self._in_blockquote = True
            self._quote_buf = ""
            self._cite_buf = ""
            return

        if self._in_blockquote and tag == "p":
            self._in_quote_p = True
            return

        if self._in_blockquote and tag == "cite":
            self._in_cite = True
            return

        if tag == "p" and cls == "" and not self._in_blockquote:
            self._in_p = True
            self._p_buf = ""
            return

        if tag == "figure":
            self._in_figure = True
            self._pending_img = None
            return

        if self._in_figure and tag == "img":
            src = a.get("src", "")
            if src.startswith("/"):
                src = SITE + src
            self._pending_img = {
                "type": "img",
                "src": src,
                "alt": a.get("alt", ""),
                "credit_name": None,
                "credit_url": None,
            }
            return

        if self._in_figure and tag == "figcaption":
            self._in_figcaption = True
            self._figcaption_buf = ""
            return

        if self._in_figcaption and tag == "a":
            self._in_credit_a = True
            self._credit_a_buf = ""
            self._credit_href = a.get("href")
            return

    def handle_endtag(self, tag):
        if self._in_head and tag == "title":
            self._in_title = False
            self.title = self._title_buf.strip()
        if tag == "head":
            self._in_head = False

        if self._in_hero and tag == "p" and self._in_breadcrumb:
            self._in_breadcrumb = False
            # breadcrumb like "Blog / Living Room" -> take last segment
            parts = [p.strip() for p in self._breadcrumb_buf.split("/")]
            if parts:
                self.category = parts[-1].strip()
        if self._in_hero and tag == "h1" and self._in_h1:
            self._in_h1 = False
            self.title = self._h1_buf.strip()
        if self._in_hero and tag == "p" and self._in_lede:
            self._in_lede = False
            self.dek = self._lede_buf.strip()
        if tag == "section" and self._in_hero:
            self._in_hero = False

        if tag == "article" and self._in_article:
            self._in_article = False
            return

        if not self._in_article:
            return

        if self._skipping:
            if tag == "div":
                self._skip_div_depth -= 1
                if self._skip_div_depth == 0:
                    self._skipping = False
            self._article_depth -= 1
            return

        if tag == "h2" and self._in_h2:
            self._in_h2 = False
            text = self._h2_buf.strip()
            if text:
                self.blocks.append({"type": "h2", "text": text})

        if tag == "div" and self._in_idea_heading:
            self._in_idea_heading = False

        if tag == "p" and self._in_p:
            self._in_p = False
            text = self._p_buf.strip()
            if text:
                self.blocks.append({"type": "p", "text": text})

        if tag == "h3" and self._in_h3:
            self._in_h3 = False
            text = self._h3_buf.strip()
            if text:
                self.blocks.append({"type": "h3", "text": text})

        if tag == "li" and self._in_li:
            self._in_li = False
            text = re.sub(r"\s+", " ", self._li_buf.strip())
            if text:
                self._list_items.append(text)

        if tag in ("ul", "ol") and self._in_list:
            self._in_list = False
            if self._list_items:
                self.blocks.append({
                    "type": "list",
                    "ordered": self._list_ordered,
                    "items": list(self._list_items),
                })
            self._list_items = []

        if self._in_blockquote and tag == "cite" and self._in_cite:
            self._in_cite = False

        if self._in_blockquote and tag == "p" and self._in_quote_p:
            self._in_quote_p = False

        if tag == "blockquote" and self._in_blockquote:
            self._in_blockquote = False
            text = re.sub(r"\s+", " ", self._quote_buf.strip())
            cite = re.sub(r"\s+", " ", self._cite_buf.strip())
            if text:
                self.blocks.append({"type": "quote", "text": text, "cite": cite or None})

        if self._in_figure and tag == "a" and self._in_credit_a:
            self._in_credit_a = False
            if self._pending_img is not None:
                self._pending_img["credit_url"] = self._credit_href

        if self._in_figure and tag == "figcaption" and self._in_figcaption:
            self._in_figcaption = False
            if self._pending_img is not None:
                text = self._figcaption_buf.strip()
                text = re.sub(r"\s+", " ", text)
                self._pending_img["credit_name"] = text or None

        if tag == "figure" and self._in_figure:
            self._in_figure = False
            if self._pending_img is not None:
                self.blocks.append(self._pending_img)
                self._pending_img = None

        self._article_depth -= 1

    def handle_data(self, data):
        if self._in_title:
            self._title_buf += data
        if self._in_breadcrumb:
            self._breadcrumb_buf += data
        if self._in_h1:
            self._h1_buf += data
        if self._in_lede:
            self._lede_buf += data
        if self._in_h2:
            self._h2_buf += data
        if self._in_h3:
            self._h3_buf += data
        if self._in_p:
            self._p_buf += data
        if self._in_li:
            self._li_buf += data
        if self._in_cite:
            self._cite_buf += data
        elif self._in_quote_p:
            self._quote_buf += data
        if self._in_figcaption:
            self._figcaption_buf += data


def main():
    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    p = ArticleParser()
    p.feed(html)

    slug = re.sub(r"\.html$", "", path.split("/")[-1])

    blocks = [
        b for b in p.blocks
        if not (b["type"] == "p" and b["text"].strip().startswith("Back to all posts"))
    ]

    out = {
        "slug": slug,
        "title": p.title,
        "dek": p.dek,
        "category": p.category,
        "blocks": blocks,
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
