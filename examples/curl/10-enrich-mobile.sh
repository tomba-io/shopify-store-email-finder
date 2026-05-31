#!/usr/bin/env bash
# 10 — Ask Tomba to attach a mobile phone number to each email where known.
# Returned in the `phone_data` array per email. Empty array = unknown / not on plan.
# Mobile enrichment is a paid add-on; free-tier keys return empty phone_data.
set -euo pipefail
. "$(dirname "$0")/_lib.sh"

curl -sG 'https://api.tomba.io/v1/domain-search' \
     --data-urlencode 'domain=allbirds.com' \
     --data-urlencode 'enrich_mobile=true' \
     --data-urlencode 'limit=5' \
     -H "X-Tomba-Key: $TOMBA_KEY" \
     -H "X-Tomba-Secret: $TOMBA_SECRET"
