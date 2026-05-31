#!/usr/bin/env bash
# 07 — Only US-based contacts (ISO 3166-1 alpha-2 country code).
# Useful when geographic targeting or compliance (e.g. CAN-SPAM vs GDPR) matters.
set -euo pipefail
. "$(dirname "$0")/_lib.sh"

curl -sG 'https://api.tomba.io/v1/domain-search' \
     --data-urlencode 'domain=allbirds.com' \
     --data-urlencode 'country=US' \
     --data-urlencode 'limit=5' \
     -H "X-Tomba-Key: $TOMBA_KEY" \
     -H "X-Tomba-Secret: $TOMBA_SECRET"
