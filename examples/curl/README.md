# Tomba API — curl example library

Every script is a single, runnable bash file that calls the live Tomba REST API. The matching `*.output.json` next to each script is the **real response** captured from `allbirds.com` — so you can see exactly what each parameter does without spending an API credit yourself.

## Running

```bash
# Load creds once
set -a; source ../../.env; set +a

# Run any example
./01-basic-search.sh

# Pretty-print
./01-basic-search.sh | jq .

# Re-capture the .output.json (refresh against the live API)
./01-basic-search.sh | python3 -m json.tool > 01-basic-search.output.json
```

## Index

### `/v1/domain-search` — bulk emails for a domain

| # | Script | What it does | Output |
|---|--------|--------------|--------|
| 01 | [01-basic-search.sh](./01-basic-search.sh) | Plain `domain=` call, first page of 10 results | [json](./01-basic-search.output.json) |
| 02 | [02-paginated.sh](./02-paginated.sh) | `page=2 & limit=5` — walk through `meta.total_pages` | [json](./02-paginated.output.json) |
| 03 | [03-personal-only.sh](./03-personal-only.sh) | `type=personal` — drop generic shared inboxes | [json](./03-personal-only.output.json) |
| 04 | [04-generic-only.sh](./04-generic-only.sh) | `type=generic` — only `info@`, `press@`, `wholesale@`, … | [json](./04-generic-only.output.json) |
| 05 | [05-by-department-executive.sh](./05-by-department-executive.sh) | `department=executive` — founders, C-suite, directors | [json](./05-by-department-executive.output.json) |
| 06 | [06-by-department-marketing.sh](./06-by-department-marketing.sh) | `department=marketing` — CMOs, growth, content | [json](./06-by-department-marketing.output.json) |
| 07 | [07-by-country-us.sh](./07-by-country-us.sh) | `country=US` — geo-filter by ISO-3166 alpha-2 | [json](./07-by-country-us.output.json) |
| 08 | [08-combined-filters.sh](./08-combined-filters.sh) | Stacked filters: US-based executives, personal-only | [json](./08-combined-filters.output.json) |
| 09 | [09-live-smtp-verify.sh](./09-live-smtp-verify.sh) | `live=true` — real-time SMTP probe per email | [json](./09-live-smtp-verify.output.json) |
| 10 | [10-enrich-mobile.sh](./10-enrich-mobile.sh) | `enrich_mobile=true` — attach phone numbers (paid add-on) | [json](./10-enrich-mobile.output.json) |

### Sibling endpoints

| # | Script | Endpoint | What it does | Output |
|---|--------|----------|--------------|--------|
| 11 | [11-email-count.sh](./11-email-count.sh) | `/v1/email-count` | Free lightweight call: totals by department + seniority | [json](./11-email-count.output.json) |
| 12 | [12-email-finder.sh](./12-email-finder.sh) | `/v1/email-finder` | Guess one person's email from `first_name + last_name + domain` | [json](./12-email-finder.output.json) |
| 13 | [13-email-verifier.sh](./13-email-verifier.sh) | `/v1/email-verifier/{email}` | Full deliverability: MX, SMTP, accept-all, disposable, score | [json](./13-email-verifier.output.json) |

## Parameter reference (`/v1/domain-search`)

| Parameter | Type | Default | Allowed values |
|-----------|------|---------|----------------|
| `domain` | string | — (required) | Any registered domain |
| `company` | string | — | Free-text company name (alternative to `domain`) |
| `page` | int | `1` | 1-indexed page number |
| `limit` | int | `10` | **Only `5`, `10`, `50`, `100`** |
| `type` | enum | `all` | `all`, `personal`, `generic` |
| `department` | string | none | `executive`, `marketing`, `sales`, `engineering`, `finance`, `hr`, `it`, `operations`, `management`, `legal`, `support`, `communication`, `accounting`, `administrative`, `diversity`, `facilities`, `pr`, `security`, `software`, `warehouse` |
| `country` | ISO-3166 | none | Two-letter country code (e.g. `US`, `GB`, `DE`) |
| `live` | bool | `false` | Triggers real-time SMTP verification per email (slower) |
| `enrich_mobile` | bool | `false` | Attach `phone_data[]` per email (paid add-on) |
| `webhook_url` | URL | none | POSTs the result to your endpoint instead of returning it |

## Notes

- All scripts read `TOMBA_KEY` and `TOMBA_SECRET` from the environment; they will error out cleanly if either is missing.
- The captured `*.output.json` files are from a live free-tier account. Personal emails are kept as-returned (public business contacts).
- Rate limit: 25 requests / second on paid plans; the free tier is lower. Add `sleep` between scripts in your own loops, or use the Python script's built-in `--rps` throttle.
