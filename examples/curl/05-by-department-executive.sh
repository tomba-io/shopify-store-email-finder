#!/usr/bin/env bash
# 05 — Only executives (founders, C-suite, directors).
# Allowed department values: executive, marketing, sales, engineering, finance,
# hr, it, operations, management, legal, support, communication, accounting,
# administrative, diversity, facilities, pr, security, software, warehouse.
set -euo pipefail
. "$(dirname "$0")/_lib.sh"

curl -sG 'https://api.tomba.io/v1/domain-search' \
     --data-urlencode 'domain=allbirds.com' \
     --data-urlencode 'department=executive' \
     --data-urlencode 'limit=5' \
     -H "X-Tomba-Key: $TOMBA_KEY" \
     -H "X-Tomba-Secret: $TOMBA_SECRET"
