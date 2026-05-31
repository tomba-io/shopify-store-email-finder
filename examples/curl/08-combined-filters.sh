#!/usr/bin/env bash
# 08 — Combine filters: US-based executives only.
# Every /domain-search filter parameter can be stacked.
set -euo pipefail
. "$(dirname "$0")/_lib.sh"

curl -sG 'https://api.tomba.io/v1/domain-search' \
     --data-urlencode 'domain=allbirds.com' \
     --data-urlencode 'department=executive' \
     --data-urlencode 'country=US' \
     --data-urlencode 'type=personal' \
     --data-urlencode 'limit=5' \
     -H "X-Tomba-Key: $TOMBA_KEY" \
     -H "X-Tomba-Secret: $TOMBA_SECRET"
