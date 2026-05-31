#!/usr/bin/env bash
# 09 — live=true triggers a real-time SMTP probe on every returned email.
# Slower (per-email handshake) but guarantees the inbox accepts mail right now.
# Use before high-stakes cold sequences.
set -euo pipefail
. "$(dirname "$0")/_lib.sh"

curl -sG 'https://api.tomba.io/v1/domain-search' \
     --data-urlencode 'domain=allbirds.com' \
     --data-urlencode 'live=true' \
     --data-urlencode 'limit=5' \
     -H "X-Tomba-Key: $TOMBA_KEY" \
     -H "X-Tomba-Secret: $TOMBA_SECRET"
