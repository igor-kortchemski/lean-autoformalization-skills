#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Read the Open Math OS team model quota through the Platform API.

Sends only `POST /v1/orgs` (when no team is given) and `POST /v1/org_model_usage`,
two read operations: no model is called and no quota is consumed. The Platform
key (a personal `nuc_oc_` key, not the `nuc_ak_` Model API key) is read from
`OPENMATHOS_PLATFORM_KEY`, or else from the macOS Keychain item of that name; it
is never printed. The Platform API is not publicly documented, so this reader
is unofficial and unsupported: not endorsed by Open Math OS, and it may break
or be refused at any time. Report a refusal or an unexpected answer instead of
guessing.
"""
import argparse
from datetime import datetime, timezone
import json
import os
import subprocess
import sys

BASE = "https://os.openmathmodel.org/v1"
KEY_NAME = "OPENMATHOS_PLATFORM_KEY"


def keychain_secret(service):
    """The macOS Keychain password stored under SERVICE for this user, or None."""
    try:
        found = subprocess.run(["security", "find-generic-password", "-a",
                                os.environ.get("USER", ""), "-s", service, "-w"],
                               capture_output=True, text=True)
    except OSError:
        return None
    return found.stdout.strip() if found.returncode == 0 else None


def call(key, operation, body, timeout):
    """POST BODY to OPERATION with curl, which uses the system certificates; the
    authorization header goes through stdin, never on the command line."""
    found = subprocess.run(
        ["curl", "-sS", "-m", str(timeout), "-X", "POST", "-H", "@-",
         "-H", "Content-Type: application/json", "--data-binary", json.dumps(body),
         "-w", "\n%{http_code}", f"{BASE}/{operation}"],
        input=f"Authorization: Bearer {key}\n", capture_output=True, text=True)
    if found.returncode != 0:
        raise RuntimeError(f"{operation}: curl failed: {found.stderr.strip()[:200]}")
    text, _, status = found.stdout.rpartition("\n")
    if status != "200":
        raise RuntimeError(f"{operation} answered {status}: {text[:200]}")
    return json.loads(text)


def window_label(name):
    return {"5h": "five-hour", "week": "weekly"}.get(name, name)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--team", help="team id (o-…); default: the only team of the key's owner")
    parser.add_argument("--json", action="store_true", help="print the normalized reading as JSON")
    parser.add_argument("--timeout", type=float, default=20, help="seconds before giving up (default 20)")
    args = parser.parse_args()
    key = os.environ.get(KEY_NAME) or keychain_secret(KEY_NAME)
    if not key:
        print(f"Open Math OS quota unavailable: no {KEY_NAME} in the environment or Keychain",
              file=sys.stderr)
        return 1
    observed = datetime.now(timezone.utc).astimezone().isoformat(timespec="minutes")
    try:
        team = args.team
        if not team:
            orgs = call(key, "orgs", {}, args.timeout).get("orgs", [])
            if len(orgs) != 1:
                raise RuntimeError(f"the key's owner has {len(orgs)} teams; pass --team")
            team = orgs[0]["id"]
        usage = call(key, "org_model_usage", {"team": team}, args.timeout)
    except (OSError, RuntimeError, KeyError, ValueError) as error:
        print(f"Open Math OS quota unavailable: {error}", file=sys.stderr)
        return 1
    report = {"observed_at": observed, "team": team, "windows": []}
    for w in usage.get("windows", []):
        limit, spent = w.get("limit_usd"), w.get("spent_usd")
        report["windows"].append({
            "window": window_label(w.get("window")),
            "limit_usd": limit,
            "spent_usd": round(spent, 2) if spent is not None else None,
            "remaining_percent": round(100 * (1 - spent / limit), 1) if limit and spent is not None else None,
            # Unrounded, for decisions such as the 5% floor; the rounded value is for display.
            "remaining_percent_exact": 100 * (1 - spent / limit) if limit and spent is not None else None,
            "resets_at": w.get("resets_at"),
        })
    if args.json:
        print(json.dumps(report, indent=2))
        return 0
    print(f"Observed at {report['observed_at']} (team {team})")
    if not report["windows"]:
        print("  no window reported")
    for w in report["windows"]:
        # An idle window (nothing spent yet) reports "resets_at": null: it has not started.
        reset = (f"resets {w['resets_at']}" if w["resets_at"] is not None
                 else "not started (no reset scheduled)")
        print(f"  {w['window']}: ${w['spent_usd']} of ${w['limit_usd']} spent,"
              f" {w['remaining_percent']}% remaining, {reset}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
