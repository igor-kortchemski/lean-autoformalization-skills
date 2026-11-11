#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Read the Codex subscription rate limits through `codex app-server`.

Sends only `initialize`, `initialized` and `account/rateLimits/read` over
JSON-RPC on stdio. It never starts a thread or turn, so no model is called and
no Codex quota is consumed. It prints no authentication data and never uses
rate-limit reset credits. Requires a Codex CLI logged in with ChatGPT.

With several Codex accounts, each logged in under its own `CODEX_HOME`, list
them in an accounts file (default `~/.config/lean-orchestrator/codex-accounts.json`):

    {"accounts": [{"name": "personal", "codex_home": "~/.codex-personal", "weight": 1},
                  {"name": "work", "codex_home": "~/.codex-work", "weight": 2}],
     "floor_percent": {"five-hour": 5, "weekly": 10}}

`weight` is the account's allowance relative to the others. `--all` reads every
account; `--choose` also picks the one to launch on: among the accounts with no
server block and every window at or above its floor, the largest
weight x (smallest headroom above a floor, in percentage points), ties going to
the earlier weekly reset. `--choose` exits with 3 when no account qualifies.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import queue
import subprocess
import sys
import tempfile
import threading
import time

READ_ID = 2
ACCOUNTS_FILE = "~/.config/lean-orchestrator/codex-accounts.json"
DEFAULT_FLOORS = {"five-hour": 5, "weekly": 10}
NO_ACCOUNT_EXIT = 3


def window_label(minutes):
    if minutes == 300:
        return "five-hour"
    if minutes == 10080:
        return "weekly"
    return f"{minutes}-minute"


def local_time(seconds):
    if seconds is None:
        return None
    return datetime.fromtimestamp(seconds, timezone.utc).astimezone().isoformat(timespec="minutes")


def read_rate_limits(codex, timeout, codex_home=None):
    env = {**os.environ, "CODEX_HOME": str(codex_home)} if codex_home else None
    with tempfile.TemporaryDirectory() as empty:
        proc = subprocess.Popen([codex, "app-server"], cwd=empty, text=True, env=env,
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL)
        lines = queue.Queue()
        threading.Thread(target=lambda: [lines.put(l) for l in proc.stdout] + [lines.put(None)],
                         daemon=True).start()
        deadline = time.monotonic() + timeout

        def send(message):
            proc.stdin.write(json.dumps(message) + "\n")
            proc.stdin.flush()

        def wait_for(request_id):
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError(f"no answer from codex app-server within {timeout} s")
                try:
                    line = lines.get(timeout=remaining)
                except queue.Empty:
                    continue
                if line is None:
                    raise RuntimeError("codex app-server exited before answering")
                try:
                    message = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(message, dict):
                    continue
                if message.get("id") == request_id and "method" not in message:
                    if "error" in message:
                        error = message["error"]
                        detail = error.get("message", error) if isinstance(error, dict) else error
                        raise RuntimeError(f"app-server error: {detail}")
                    return message["result"]

        try:
            send({"method": "initialize", "id": 1,
                  "params": {"clientInfo": {"name": "lean_orchestrator_quota",
                                            "title": "Lean orchestrator quota check",
                                            "version": "1.0.0"}}})
            wait_for(1)
            send({"method": "initialized", "params": {}})
            send({"method": "account/rateLimits/read", "id": READ_ID})
            return wait_for(READ_ID)
        finally:
            proc.stdin.close()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()


def summarize(result, observed):
    limits = result.get("rateLimitsByLimitId") or {}
    if not limits and result.get("rateLimits"):
        fallback = result["rateLimits"]
        limits = {fallback.get("limitId") or "codex": fallback}
    report = {"observed_at": observed.astimezone().isoformat(timespec="seconds"),
              "ordinary_usage_allowed": result.get("ordinaryUsageAllowed"),
              "server_block": result.get("ordinaryUsageAllowed") is False,
              "limits": []}
    for limit_id, limit in limits.items():
        windows = []
        for slot in ("primary", "secondary"):
            window = limit.get(slot)
            if not window:
                continue
            used = window.get("usedPercent")
            minutes = window.get("windowDurationMins")
            windows.append({
                "window": window_label(minutes) if minutes else "unknown",
                "duration_minutes": minutes,
                "used_percent": used,
                "remaining_percent": None if used is None else max(0, min(100, 100 - used)),
                "resets_at": local_time(window.get("resetsAt")),
            })
        credits = limit.get("credits") or {}
        if limit.get("spendControlReached") or limit.get("rateLimitReachedType"):
            report["server_block"] = True
        report["limits"].append({
            "limit_id": limit_id,
            "limit_name": limit.get("limitName"),
            "plan_type": limit.get("planType"),
            "windows": windows,
            "limit_reached": limit.get("rateLimitReachedType"),
            "spend_control_reached": limit.get("spendControlReached"),
            "credits_balance": credits.get("balance"),
            "credits_unlimited": credits.get("unlimited"),
        })
    return report


def load_accounts(path):
    """The registered accounts, each with its expanded `codex_home`, and the floors per window."""
    data = json.loads(Path(path).expanduser().read_text())
    accounts = []
    for account in data["accounts"]:
        home = Path(account["codex_home"]).expanduser()
        accounts.append({"name": account["name"], "codex_home": str(home),
                         "weight": float(account.get("weight", 1))})
    if len({a["name"] for a in accounts}) != len(accounts) or not accounts:
        raise ValueError(f"{path}: account names must be present and distinct")
    return accounts, {**DEFAULT_FLOORS, **data.get("floor_percent", {})}


def assess(account, report, floors):
    """Add the account's headroom above its floors and its score to its reading."""
    windows = [w for limit in report["limits"] for w in limit["windows"]]
    headroom = [w["remaining_percent"] - floors.get(w["window"], 0) for w in windows
                if w["remaining_percent"] is not None]
    weekly = [w["resets_at"] for w in windows if w["window"] == "weekly" and w["resets_at"]]
    account["reading"] = report
    account["headroom"] = min(headroom) if headroom else None
    account["eligible"] = (not report["server_block"] and account["headroom"] is not None
                           and account["headroom"] >= 0)
    account["score"] = account["weight"] * account["headroom"] if account["eligible"] else None
    account["weekly_reset"] = min(weekly) if weekly else None
    return account


def choose(accounts):
    """The eligible account with the most weighted headroom, ties to the earlier weekly reset."""
    eligible = [a for a in accounts if a["eligible"]]
    if not eligible:
        return None
    return min(eligible, key=lambda a: (-a["score"], a["weekly_reset"] or "9999"))


def read_accounts(args):
    accounts, floors = load_accounts(args.accounts)
    for account in accounts:
        observed = datetime.now(timezone.utc)
        try:
            report = summarize(read_rate_limits(args.codex, args.timeout, account["codex_home"]), observed)
        except (OSError, RuntimeError, TimeoutError, KeyError) as error:
            account.update(reading=None, error=str(error), eligible=False, score=None)
            continue
        assess(account, report, floors)
    chosen = choose(accounts) if args.choose else None
    result = {"floor_percent": floors, "accounts": accounts}
    if args.choose:
        result["chosen"] = chosen and chosen["name"]
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for a in accounts:
            if a.get("error"):
                print(f"{a['name']} ({a['codex_home']}): unreadable: {a['error']}")
                continue
            print(f"{a['name']} (weight {a['weight']:g}): headroom {a['headroom']} points above the floor, "
                  f"{'eligible' if a['eligible'] else 'NOT eligible'}"
                  f"{', SERVER BLOCK' if a['reading']['server_block'] else ''}, weekly reset {a['weekly_reset']}")
        if args.choose:
            print(f"chosen: {result['chosen'] or 'none'}")
    return NO_ACCOUNT_EXIT if args.choose and not chosen else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", action="store_true", help="print the normalized reading as JSON")
    parser.add_argument("--timeout", type=float, default=20, help="seconds before giving up (default 20)")
    parser.add_argument("--codex", default="codex", help="Codex CLI executable")
    parser.add_argument("--all", action="store_true", help="read every account of the accounts file")
    parser.add_argument("--choose", action="store_true",
                        help="read every account and pick the one to launch on (exit 3: none qualifies)")
    parser.add_argument("--accounts", default=ACCOUNTS_FILE, help=f"accounts file (default {ACCOUNTS_FILE})")
    args = parser.parse_args()
    if args.all or args.choose:
        try:
            return read_accounts(args)
        except (OSError, ValueError, KeyError, TypeError) as error:
            print(f"accounts file unusable: {error}", file=sys.stderr)
            return 1
    observed = datetime.now(timezone.utc)
    try:
        report = summarize(read_rate_limits(args.codex, args.timeout), observed)
    except (OSError, RuntimeError, TimeoutError, KeyError) as error:
        print(f"Codex quota unavailable: {error}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(report, indent=2))
        return 0
    print(f"Observed at {report['observed_at']}")
    if report["server_block"]:
        print("SERVER BLOCK: the server refuses or limits ordinary usage"
              f" (ordinaryUsageAllowed={report['ordinary_usage_allowed']}); launch no Codex work")
    for limit in report["limits"]:
        print(f"{limit['limit_id']} (plan {limit['plan_type']}):")
        if not limit["windows"]:
            print("  no window reported")
        for w in limit["windows"]:
            print(f"  {w['window']}: {w['used_percent']}% used, {w['remaining_percent']}% remaining,"
                  f" resets {w['resets_at']}")
        if limit["limit_reached"]:
            print(f"  limit reached: {limit['limit_reached']}")
        if limit["spend_control_reached"]:
            print("  spend control reached")
    return 0


if __name__ == "__main__":
    sys.exit(main())
