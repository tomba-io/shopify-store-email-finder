#!/usr/bin/env bash
# 11 — /email-count: how many emails Tomba has for a domain, broken down by
# department and seniority. Free + lightweight — use it to qualify a domain
# before spending a /domain-search credit.
set -euo pipefail
. "$(dirname "$0")/_lib.sh"

curl -sG 'https://api.tomba.io/v1/email-count' \
     --data-urlencode 'domain=allbirds.com' \
     -H "X-Tomba-Key: $TOMBA_KEY" \
     -H "X-Tomba-Secret: $TOMBA_SECRET"
