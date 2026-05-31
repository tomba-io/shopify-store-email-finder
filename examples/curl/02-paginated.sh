#!/usr/bin/env bash
# 02 — Pagination through a large store's contact list.
# Tomba returns meta.total_pages — walk it with `page` (1-indexed) until you hit the end.
# Allowed limit values: 5, 10, 50, 100.
set -euo pipefail
. "$(dirname "$0")/_lib.sh"

curl -sG 'https://api.tomba.io/v1/domain-search' \
     --data-urlencode 'domain=allbirds.com' \
     --data-urlencode 'page=2' \
     --data-urlencode 'limit=5' \
     -H "X-Tomba-Key: $TOMBA_KEY" \
     -H "X-Tomba-Secret: $TOMBA_SECRET"
