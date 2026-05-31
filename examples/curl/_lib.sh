#!/usr/bin/env bash
# Shared helpers for every example script.
# Source this from each example: . "$(dirname "$0")/_lib.sh"

# Walk up from PWD finding the nearest .env, then source its KEY=VALUE pairs.
# Existing env vars always win (.env never overrides what's already exported).
load_dotenv() {
  local d="$PWD"
  while [[ "$d" != "/" ]]; do
    if [[ -f "$d/.env" ]]; then
      set -a
      # shellcheck disable=SC1091
      . "$d/.env"
      set +a
      return 0
    fi
    d="$(dirname "$d")"
  done
  return 1
}

load_dotenv || true

: "${TOMBA_KEY:?TOMBA_KEY missing — set it in your env or a .env file. Get a free key at https://app.tomba.io}"
: "${TOMBA_SECRET:?TOMBA_SECRET missing — set it in your env or a .env file. Get a free key at https://app.tomba.io}"
