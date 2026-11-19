#!/bin/sh
# Usage: pull_list.sh <list-path>
# Runs on the Hostinger server. Fetches a repo file listing one path per line
# (e.g. scripts/deploy/lists/pins-2026-11-19.txt) and pulls every listed file
# into public_html. Use when there are too many paths for a 255-char cron command.
set -u
REPO="Shahroz101/sarahshahroz-site"
ROOT="/home/u218614123/domains/sarahshahroz.com/public_html"

cd "$ROOT" || exit 1

list=$(curl -sfL "https://raw.githubusercontent.com/$REPO/main/$1") || { echo "FAIL list $1"; exit 1; }

ok=0; fail=0
for p in $list; do
  mkdir -p "$(dirname "$p")"
  if curl -sfL "https://raw.githubusercontent.com/$REPO/main/$p" -o "$p.tmp" && mv "$p.tmp" "$p"; then
    ok=$((ok+1))
  else
    fail=$((fail+1)); echo "FAIL $p"; rm -f "$p.tmp"
  fi
done

echo "OK $ok FAIL $fail"
