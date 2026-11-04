#!/bin/sh
# Usage: pull_file.sh <path> [<path> ...]
# Runs on the Hostinger server. Pulls the named repo files (relative to the
# repo root, e.g. .htaccess or css/style.css) from GitHub into public_html.
set -u
REPO="Shahroz101/sarahshahroz-site"
ROOT="/home/u218614123/domains/sarahshahroz.com/public_html"

cd "$ROOT" || exit 1

ok=0; fail=0
for p in "$@"; do
  mkdir -p "$(dirname "$p")"
  if curl -sfL "https://raw.githubusercontent.com/$REPO/main/$p" -o "$p.tmp" && mv "$p.tmp" "$p"; then
    ok=$((ok+1)); echo "OK $p"
  else
    fail=$((fail+1)); echo "FAIL $p"; rm -f "$p.tmp"
  fi
done

echo "OK $ok FAIL $fail"
