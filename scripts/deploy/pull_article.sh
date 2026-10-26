#!/bin/sh
# Usage: pull_article.sh <slug>
# Runs on the Hostinger server. Pulls one article's files (page, images,
# archive index, homepage) from the public GitHub repo into public_html.
set -u
SLUG="$1"
REPO="Shahroz101/sarahshahroz-site"
ROOT="/home/u218614123/domains/sarahshahroz.com/public_html"
LIST="$HOME/deploy_${SLUG}.txt"

cd "$ROOT" || exit 1

curl -s "https://api.github.com/repos/$REPO/git/trees/main?recursive=1" \
  | grep -o '"path": *"[^"]*"' \
  | sed 's/"path": *"//;s/"$//' \
  | grep -E "^(${SLUG}\.html|index\.html|articles/index\.html|css/style\.css|js/script\.js|images/articles/${SLUG}/.*\.(jpg|jpeg|png|webp))$" \
  > "$LIST"

ok=0; fail=0
while read -r p; do
  mkdir -p "$(dirname "$p")"
  if curl -sfL "https://raw.githubusercontent.com/$REPO/main/$p" -o "$p.tmp" && mv "$p.tmp" "$p"; then
    ok=$((ok+1))
  else
    fail=$((fail+1)); echo "FAIL $p"; rm -f "$p.tmp"
  fi
done < "$LIST"

echo "LISTED $(wc -l < "$LIST" | tr -d ' ') OK $ok FAIL $fail"
