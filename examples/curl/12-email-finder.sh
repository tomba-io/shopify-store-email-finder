#!/usr/bin/env bash
# 12 — /email-finder: guess the email for one named person at a domain.
# Returns the most likely address + score + position + verification status.
# Use when you already have a first+last name (e.g. from a LinkedIn export).
set -euo pipefail
. "$(dirname "$0")/_lib.sh"

curl -sG 'https://api.tomba.io/v1/email-finder' \
     --data-urlencode 'domain=allbirds.com' \
     --data-urlencode 'first_name=Tess' \
     --data-urlencode 'last_name=Haas' \
     -H "X-Tomba-Key: $TOMBA_KEY" \
     -H "X-Tomba-Secret: $TOMBA_SECRET"
