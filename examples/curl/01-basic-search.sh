#!/usr/bin/env bash
# 01 — Basic /domain-search call.
# Returns the first page (10 results) of every email Tomba has for the domain.
# Required:  domain
set -euo pipefail
. "$(dirname "$0")/_lib.sh"

curl -sG 'https://api.tomba.io/v1/domain-search' \
     --data-urlencode 'domain=allbirds.com' \
     -H "X-Tomba-Key: $TOMBA_KEY" \
     -H "X-Tomba-Secret: $TOMBA_SECRET"
