#!/usr/bin/env bash
# 04 — Filter to generic / shared inboxes only (info@, support@, press@, wholesale@, ...).
# Useful for press outreach, partnership requests, or wholesale inquiries.
set -euo pipefail
. "$(dirname "$0")/_lib.sh"

curl -sG 'https://api.tomba.io/v1/domain-search' \
     --data-urlencode 'domain=allbirds.com' \
     --data-urlencode 'type=generic' \
     --data-urlencode 'limit=5' \
     -H "X-Tomba-Key: $TOMBA_KEY" \
     -H "X-Tomba-Secret: $TOMBA_SECRET"
