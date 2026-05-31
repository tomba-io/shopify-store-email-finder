#!/usr/bin/env bash
# 03 — Filter to person-attached emails only (excludes info@, support@, ...).
# Use when you're doing 1:1 outreach and don't want shared inboxes.
# Allowed type values: all (default), personal, generic.
set -euo pipefail
. "$(dirname "$0")/_lib.sh"

curl -sG 'https://api.tomba.io/v1/domain-search' \
     --data-urlencode 'domain=allbirds.com' \
     --data-urlencode 'type=personal' \
     --data-urlencode 'limit=5' \
     -H "X-Tomba-Key: $TOMBA_KEY" \
     -H "X-Tomba-Secret: $TOMBA_SECRET"
