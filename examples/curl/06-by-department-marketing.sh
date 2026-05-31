#!/usr/bin/env bash
# 06 — Only marketing-department contacts (CMOs, growth, content, brand).
# Often the right department to pitch agencies, tools, and influencer programs to.
set -euo pipefail
. "$(dirname "$0")/_lib.sh"

curl -sG 'https://api.tomba.io/v1/domain-search' \
     --data-urlencode 'domain=allbirds.com' \
     --data-urlencode 'department=marketing' \
     --data-urlencode 'limit=5' \
     -H "X-Tomba-Key: $TOMBA_KEY" \
     -H "X-Tomba-Secret: $TOMBA_SECRET"
