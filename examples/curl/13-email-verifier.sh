#!/usr/bin/env bash
# 13 — /email-verifier/{email}: full deliverability check on a single address.
# Returns MX records, SMTP-server check, accept-all flag, disposable flag,
# webmail flag, gibberish detector, and a 0-100 score.
set -euo pipefail
. "$(dirname "$0")/_lib.sh"

curl -sG 'https://api.tomba.io/v1/email-verifier/nick.polesky@allbirds.com' \
     -H "X-Tomba-Key: $TOMBA_KEY" \
     -H "X-Tomba-Secret: $TOMBA_SECRET"
