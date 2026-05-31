"""Find contact emails behind Shopify store domains using the Tomba API.

Three building blocks:

    find_emails_by_store(domains)            -> bulk /domain-search
    find_specific_person(domain, first, last) -> targeted /email-finder
    verify_email(email)                      -> /email-verifier

Run as a CLI for stdout JSON:

    python shopify_emails.py allbirds.com bombas.com
    cat examples/shopify-stores.txt | python shopify_emails.py --csv > emails.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator
from urllib.parse import urlparse

import requests


def _load_dotenv() -> Path | None:
    """Walk up from CWD finding the nearest .env and load its KEY=VALUE pairs.

    Existing environment variables always win — .env never overrides what's
    already exported. Returns the path of the file loaded, or None.
    """
    cwd = Path.cwd().resolve()
    for d in (cwd, *cwd.parents):
        env_path = d / ".env"
        if not env_path.is_file():
            continue
        for raw in env_path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip()
            if (val.startswith('"') and val.endswith('"')) or (
                val.startswith("'") and val.endswith("'")
            ):
                val = val[1:-1]
            os.environ.setdefault(key, val)
        return env_path
    return None

API_BASE = "https://api.tomba.io/v1"
DEFAULT_RPS = 5
USER_AGENT = "tomba-shopify-store-email-finder/0.1.0 (+https://github.com/tomba-io)"
# Tomba /domain-search only accepts these page sizes
VALID_LIMITS = (5, 10, 50, 100)


def snap_limit(n: int) -> int:
    """Round n up to the nearest Tomba-allowed page size."""
    for v in VALID_LIMITS:
        if n <= v:
            return v
    return VALID_LIMITS[-1]


class TombaAuthError(RuntimeError):
    pass


class TombaAPIError(RuntimeError):
    pass


@dataclass(frozen=True)
class Credentials:
    key: str
    secret: str

    @classmethod
    def from_env(cls) -> "Credentials":
        _load_dotenv()
        key = os.environ.get("TOMBA_KEY", "").strip()
        secret = os.environ.get("TOMBA_SECRET", "").strip()
        if not key or not secret:
            raise TombaAuthError(
                "TOMBA_KEY and TOMBA_SECRET must be set in your environment "
                "or in a .env file (searched from the current directory up). "
                "Get a free key at https://app.tomba.io"
            )
        return cls(key=key, secret=secret)


class TombaClient:
    """Thin Tomba REST client with one Session and built-in throttle."""

    def __init__(self, creds: Credentials, rps: float = DEFAULT_RPS) -> None:
        self._creds = creds
        self._min_interval = 1.0 / rps if rps > 0 else 0.0
        self._last_call = 0.0
        self._session = requests.Session()
        self._session.headers.update(
            {
                "X-Tomba-Key": creds.key,
                "X-Tomba-Secret": creds.secret,
                "User-Agent": USER_AGENT,
                "Accept": "application/json",
            }
        )

    def _throttle(self) -> None:
        if self._min_interval <= 0:
            return
        elapsed = time.monotonic() - self._last_call
        wait = self._min_interval - elapsed
        if wait > 0:
            time.sleep(wait)
        self._last_call = time.monotonic()

    def get(self, path: str, params: dict | None = None) -> dict:
        self._throttle()
        url = f"{API_BASE}{path}"
        resp = self._session.get(url, params=params or {}, timeout=30)
        if resp.status_code == 401:
            raise TombaAuthError("Invalid TOMBA_KEY / TOMBA_SECRET (401)")
        if resp.status_code == 429:
            raise TombaAPIError(
                "Tomba rate limit hit (429). Lower --rps or upgrade your plan."
            )
        if resp.status_code >= 400:
            raise TombaAPIError(f"{resp.status_code} {resp.text[:200]}")
        try:
            return resp.json()
        except ValueError as exc:
            raise TombaAPIError(f"Non-JSON response from {path}: {exc}") from exc


def normalize_domain(value: str) -> str:
    """allbirds.com / https://allbirds.com / shop.allbirds.com -> bare host."""
    text = value.strip()
    if not text:
        return ""
    if "://" not in text:
        text = f"https://{text}"
    host = (urlparse(text).hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def find_emails_by_store(
    domains: Iterable[str],
    *,
    client: TombaClient | None = None,
    limit_per_store: int = 10,
) -> list[dict]:
    """For each Shopify store domain, return a flat list of contact records.

    Each record has the fields documented in the README's Output Fields table.
    """
    client = client or TombaClient(Credentials.from_env())
    page_size = snap_limit(limit_per_store)
    records: list[dict] = []
    for raw in domains:
        domain = normalize_domain(raw)
        if not domain:
            continue
        try:
            payload = client.get(
                "/domain-search",
                params={"domain": domain, "limit": page_size},
            )
        except TombaAPIError as exc:
            records.append(_error_record(domain, str(exc)))
            continue
        records.extend(_records_from_domain_search(domain, payload))
    return records


def find_specific_person(
    domain: str,
    first_name: str,
    last_name: str,
    *,
    client: TombaClient | None = None,
) -> dict:
    """Targeted lookup: guess the likely email for one named person at a domain."""
    client = client or TombaClient(Credentials.from_env())
    payload = client.get(
        "/email-finder",
        params={
            "domain": normalize_domain(domain),
            "first_name": first_name,
            "last_name": last_name,
        },
    )
    email = (payload.get("data") or {}).get("email") or {}
    if isinstance(email, list):
        email = email[0] if email else {}
    return {
        "domain": normalize_domain(domain),
        "first_name": first_name,
        "last_name": last_name,
        "email": email.get("email", ""),
        "score": email.get("score"),
        "position": email.get("position", ""),
        "department": email.get("department", ""),
    }


def verify_email(email: str, *, client: TombaClient | None = None) -> dict:
    """Verify deliverability of a single email."""
    client = client or TombaClient(Credentials.from_env())
    payload = client.get(f"/email-verifier/{email}")
    result = ((payload.get("data") or {}).get("email")) or {}
    return {
        "email": email,
        "result": result.get("result", ""),
        "score": result.get("score"),
        "regexp": result.get("regexp"),
        "gibberish": result.get("gibberish"),
        "disposable": result.get("disposable"),
        "webmail": result.get("webmail"),
        "mx_records": result.get("mx_records"),
        "smtp_server": result.get("smtp_server"),
        "smtp_check": result.get("smtp_check"),
        "accept_all": result.get("accept_all"),
        "block": result.get("block"),
        "status": result.get("status", ""),
    }


def _records_from_domain_search(domain: str, payload: dict) -> Iterator[dict]:
    data = payload.get("data") or {}
    org = data.get("organization") or {}
    for entry in data.get("emails") or []:
        verification = entry.get("verification") or {}
        yield {
            "store": org.get("organization") or domain,
            "domain": domain,
            "email": entry.get("email", ""),
            "first_name": entry.get("first_name", ""),
            "last_name": entry.get("last_name", ""),
            "full_name": entry.get("full_name", ""),
            "position": entry.get("position", ""),
            "department": entry.get("department", ""),
            "seniority": entry.get("seniority", ""),
            "type": entry.get("type", ""),
            "country": entry.get("country", ""),
            "linkedin": entry.get("linkedin", ""),
            "twitter": entry.get("twitter", ""),
            "score": entry.get("score"),
            "verification_status": verification.get("status", ""),
            "industries": org.get("industries", ""),
            "company_size": org.get("company_size", ""),
            "founded": org.get("founded", ""),
            "error": "",
        }


def _error_record(domain: str, message: str) -> dict:
    return {
        "store": "",
        "domain": domain,
        "email": "",
        "first_name": "",
        "last_name": "",
        "full_name": "",
        "position": "",
        "department": "",
        "seniority": "",
        "type": "",
        "country": "",
        "linkedin": "",
        "twitter": "",
        "score": None,
        "verification_status": "",
        "industries": "",
        "company_size": "",
        "founded": "",
        "error": message,
    }


def _read_domain_args(args_list: list[str]) -> list[str]:
    if args_list:
        return args_list
    if sys.stdin.isatty():
        return []
    return [line for line in (l.strip() for l in sys.stdin) if line]


def _write_csv(records: list[dict], stream) -> None:
    if not records:
        return
    fieldnames = list(records[0].keys())
    writer = csv.DictWriter(stream, fieldnames=fieldnames)
    writer.writeheader()
    for r in records:
        writer.writerow(r)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="shopify_emails",
        description="Find contact emails behind Shopify store domains (Tomba API).",
    )
    parser.add_argument(
        "domains",
        nargs="*",
        help="Shopify store domains (e.g. allbirds.com). Reads stdin if empty.",
    )
    parser.add_argument("--csv", action="store_true", help="Output CSV instead of JSON.")
    parser.add_argument(
        "--limit", type=int, default=10, help="Max emails per store (default 10)."
    )
    parser.add_argument(
        "--rps",
        type=float,
        default=float(os.environ.get("TOMBA_RPS", DEFAULT_RPS)),
        help="Throttle: requests per second (default 5).",
    )
    parser.add_argument("--version", action="version", version="0.1.0")
    args = parser.parse_args(argv)

    domains = _read_domain_args(args.domains)
    if not domains:
        parser.error("provide at least one domain (arg or stdin)")

    try:
        creds = Credentials.from_env()
    except TombaAuthError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    client = TombaClient(creds, rps=args.rps)
    records = find_emails_by_store(
        domains, client=client, limit_per_store=args.limit
    )

    if args.csv:
        _write_csv(records, sys.stdout)
    else:
        json.dump(records, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
