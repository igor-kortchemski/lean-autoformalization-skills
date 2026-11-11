#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Count the tokens each agent of a campaign used, from the records on disk.

`register` notes the current Claude Code session (CLAUDE_CODE_SESSION_ID, or
`--session`) in `PROJECT/.orchestration/claude-sessions.json`, from now on;
`register --end` closes that period. Run it at campaign setup and at each
resumption in a new session, and with `--end` when a session leaves the campaign.

`report` prints one row per agent, model and effort, with token counts only:
- Claude: the coordinator's own messages and each subagent's, read from Claude
  Code's transcripts of the registered sessions (and of `--claude-session`, counted
  whole), within the registered periods. Each API message is counted once, also
  when a copied or forked session repeats it.
- Codex workers: `settings.json` of every `attempt-N` folder under
  `PROJECT/.orchestration`. A resumed session's total includes the attempts it
  resumed, so each attempt counts only its difference with the session's total
  before it started (recorded by the launcher since version 2.0.0) or, failing
  that, with the previous counted attempt of the same session; a resumed attempt
  with neither is listed, not counted.
- Open Math OS VM workers: `usage.json` of every run folder, written by
  `vm_worker.py wait` or `status`. The VM does not split cached input
  tokens or reasoning tokens: those cells read "not recorded".
Input tokens include cached ones; output tokens include reasoning ones. Anything
that could not be counted is listed under the table. Reads files only.
Standard library only.
"""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys

FIELDS = ("input", "cached", "cache_write", "output", "reasoning")
HEADERS = ("Input tokens", "of which cached", "Cache writes", "Output tokens", "of which reasoning")
SKIP_DIRS = {".git", ".lake", "node_modules", "__pycache__"}


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def parse_time(text):
    if not text:
        return None
    try:
        moment = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    return moment if moment.tzinfo else moment.replace(tzinfo=timezone.utc)


def sessions_file(project):
    return Path(project) / ".orchestration" / "claude-sessions.json"


def read_json(path):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return None


def register(args):
    session = args.session or os.environ.get("CLAUDE_CODE_SESSION_ID")
    if not session or not re.fullmatch(r"[0-9a-fA-F-]{8,64}", session):
        print("token_ledger: no Claude Code session id (CLAUDE_CODE_SESSION_ID); pass --session",
              file=sys.stderr)
        return 1
    path = sessions_file(args.project)
    data = read_json(path) or {"sessions": []}
    periods = [p for p in data["sessions"] if p["id"] == session]
    open_period = next((p for p in periods if p.get("until") is None), None)
    if args.end:
        if open_period is None:
            print(json.dumps({"session": session, "note": "no open period to end"}))
            return 0
        open_period["until"] = now()
    elif open_period is None:
        data["sessions"].append({"id": session, "from": now(), "until": None})
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(".claude-sessions.json.tmp")
    tmp.write_text(json.dumps(data, indent=1) + "\n")
    os.replace(tmp, path)
    print(json.dumps({"session": session, "periods": [p for p in data["sessions"] if p["id"] == session]}))
    return 0


class Ledger:
    def __init__(self, since=None, until=None):
        self.rows = defaultdict(lambda: {"count": 0, **{f: 0 for f in FIELDS},
                                         "unrecorded": set(), "partial": set()})
        self.missing = []
        self.since, self.until = since, until

    def in_window(self, moment):
        if moment is None:
            return self.since is None and self.until is None
        return (self.since is None or moment >= self.since) and (self.until is None or moment <= self.until)

    def add(self, key, usage, count=1):
        """USAGE maps each field to a count, or to None when the source does not record it."""
        row = self.rows[key]
        row["count"] += count
        for f in FIELDS:
            value = usage.get(f)
            if value is None:
                row["unrecorded"].add(f)
            else:
                row[f] += value


# Claude Code transcripts

def claude_root():
    return Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude") / "projects"


def transcript_rows(path):
    try:
        with open(path, errors="replace") as handle:
            for line in handle:
                try:
                    entry = json.loads(line, strict=False)
                except ValueError:
                    continue
                if isinstance(entry, dict):
                    yield entry
    except OSError:
        return


def claude_messages(path, periods, counted):
    """Assistant messages of a transcript inside PERIODS, once per API message id.

    COUNTED holds the ids already counted from other transcripts: a copied or forked
    session repeats its source's messages with the same ids."""
    found = {}
    for entry in transcript_rows(path):
        message = entry.get("message")
        if entry.get("type") != "assistant" or not isinstance(message, dict):
            continue
        usage, model = message.get("usage"), message.get("model")
        if not isinstance(usage, dict) or model in (None, "<synthetic>"):
            continue
        moment = parse_time(entry.get("timestamp"))
        if periods is not None and not any(
                moment is not None and (start is None or moment >= start) and (end is None or moment <= end)
                for start, end in periods):
            continue
        key = message.get("id") or entry.get("uuid")
        if key in counted:
            continue
        found[key] = (moment, model, entry.get("effort"), usage)
    counted.update(found)
    return found.values()


def claude_usage(usage):
    fresh = usage.get("input_tokens") or 0
    write = usage.get("cache_creation_input_tokens") or 0
    read = usage.get("cache_read_input_tokens") or 0
    details = usage.get("output_tokens_details")
    reasoning = details.get("thinking_tokens") if isinstance(details, dict) else None
    return {"input": fresh + write + read, "cached": read, "cache_write": write,
            "output": usage.get("output_tokens") or 0, "reasoning": reasoning}


def add_claude(ledger, sessions):
    root = claude_root()
    counted = set()
    for session, periods in sessions.items():
        mains = sorted(root.glob(f"*/{session}.jsonl"))
        if not mains:
            ledger.missing.append(f"Claude session {session}: no transcript under {root}")
            continue
        for main in mains:
            files = [(main, None)] + [(p, p.with_name(p.stem + ".meta.json"))
                                      for p in sorted((main.parent / session / "subagents").glob("agent-*.jsonl"))]
            for path, meta_path in files:
                if meta_path is None:
                    agent = "coordinator"
                else:
                    meta = read_json(meta_path) or {}
                    agent = f"subagent {meta.get('agentType') or 'unknown type'}"
                seen = set()
                for moment, model, effort, usage in claude_messages(path, periods, counted):
                    if not ledger.in_window(moment):
                        continue
                    key = ("Claude", agent, model, effort or "not recorded")
                    # A row counts sessions for the coordinator, subagents otherwise.
                    first = key not in seen
                    seen.add(key)
                    ledger.add(key, claude_usage(usage), count=1 if first else 0)


# Codex workers

def attempt_dirs(orchestration):
    for parent, dirs, names in os.walk(orchestration):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        if re.fullmatch(r"attempt-\d+", Path(parent).name):
            dirs[:] = []
            yield Path(parent)


def codex_usage(usage):
    def get(*names):
        for name in names:
            if isinstance(usage.get(name), (int, float)):
                return usage[name]
        return None
    return {"input": get("input_tokens"), "cached": get("cached_input_tokens"),
            "cache_write": get("cache_write_input_tokens"), "output": get("output_tokens"),
            "reasoning": get("reasoning_output_tokens")}


def add_codex(ledger, orchestration):
    attempts = []
    for attempt in attempt_dirs(orchestration):
        settings = read_json(attempt / "settings.json")
        process = read_json(attempt / "process.json") or {}
        launched = parse_time(process.get("launched_at"))
        if settings is None:
            if not ledger.in_window(launched):
                continue
            state = "finished" if (attempt / "exit-status").exists() else "still running or interrupted"
            ledger.missing.append(f"Codex attempt {attempt.relative_to(orchestration)}: no settings.json ({state})")
            continue
        attempts.append((launched, attempt, settings, process))
    # A resumed session keeps counting: subtract the previous attempt of the same session log,
    # also when that attempt falls outside --since and --until.
    previous = {}
    for launched, attempt, settings, process in sorted(attempts, key=lambda a: (a[0] or datetime.min.replace(
            tzinfo=timezone.utc), str(a[1]))):
        requested, observed = settings.get("requested", {}), settings.get("observed", {})
        model = (observed.get("model") or [None])[-1] if len(observed.get("model") or []) == 1 \
            else requested.get("model")
        effort = (observed.get("effort") or [None])[-1] if len(observed.get("effort") or []) == 1 \
            else requested.get("effort")
        provider = requested.get("provider")
        agent = "Codex worker via Open Math OS" if provider == "openmathos" else "Codex worker"
        name = str(attempt.relative_to(orchestration))
        if not isinstance(settings.get("usage"), dict):
            if ledger.in_window(launched):
                ledger.missing.append(f"Codex attempt {name}: no usage recorded")
            continue
        usage = codex_usage(settings["usage"])
        log = settings.get("session_log")
        total_scope = settings.get("usage_scope") == "Codex session total when the attempt ended"
        resumed = bool(settings.get("requested", {}).get("resume") or settings.get("session_log_from_byte")
                       or "resume" in (process.get("command") or []))
        if total_scope and log:
            if isinstance(settings.get("usage_before_attempt"), dict):
                before = codex_usage(settings["usage_before_attempt"])
            else:
                before = previous.get(log)
            previous[log] = usage
            if resumed and before is None:
                if ledger.in_window(launched):
                    ledger.missing.append(f"Codex attempt {name}: resumed session with no counted "
                                          f"earlier attempt; its total includes them, not counted")
                continue
            if before:
                usage = {f: None if usage[f] is None or before[f] is None else usage[f] - before[f]
                         for f in FIELDS}
                if any(v is not None and v < 0 for v in usage.values()):
                    if ledger.in_window(launched):
                        ledger.missing.append(f"Codex attempt {name}: session total below the previous attempt's")
                    continue
        elif settings.get("usage_scope") != "Codex session total when the attempt ended" \
                and ledger.in_window(launched):
            ledger.missing.append(f"Codex attempt {name}: counted from its last turn only "
                                  f"(no session log)")
        if ledger.in_window(launched):
            ledger.add(("Codex", agent, model or "not recorded", effort or "not recorded"), usage)


# Open Math OS VM workers

def add_vm(ledger, orchestration):
    for parent, dirs, names in os.walk(orchestration):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        if "run.json" not in names:
            continue
        run_dir = Path(parent)
        name = str(run_dir.relative_to(orchestration)) or "."
        record = read_json(run_dir / "run.json") or {}
        if "project" not in record:
            continue
        if not ledger.in_window(parse_time(record.get("sent_at"))):
            continue
        usage = read_json(run_dir / "usage.json")
        if not usage:
            ledger.missing.append(f"VM run {name}: no usage.json (run `vm_worker.py status --run-dir` on it)")
            continue
        if not usage.get("complete"):
            ledger.missing.append(f"VM run {name}: usage.json saved while the run was still going "
                                  f"({usage.get('observed_at')})")
        for effort, row in sorted((usage.get("by_effort") or {}).items()):
            ledger.add(("Open Math OS VM", "hosted agent", usage.get("model") or record.get("model")
                        or "not recorded", effort),
                       {"input": row.get("input_tokens"), "cached": None, "cache_write": None,
                        "output": row.get("output_tokens"), "reasoning": None})


def cell(row, field):
    if field in row["unrecorded"]:
        return "not recorded" if row[field] == 0 else f"{row[field]:,} (partial)"
    return f"{row[field]:,}"


def table(ledger):
    lines = ["| Source | Agent | Model | Effort | Count | " + " | ".join(HEADERS) + " | Total |",
             "| --- | --- | --- | --- | ---: | " + " | ".join("---:" for _ in HEADERS) + " | ---: |"]
    totals = defaultdict(lambda: {"count": 0, **{f: 0 for f in FIELDS}, "unrecorded": set()})
    for key in sorted(ledger.rows, key=lambda k: tuple(str(x) for x in k)):
        row = ledger.rows[key]
        lines.append("| " + " | ".join(str(x) for x in key) + f" | {row['count']} | "
                     + " | ".join(cell(row, f) for f in FIELDS) + f" | {row['input'] + row['output']:,} |")
        for scope in (key[0], "All sources"):
            total = totals[scope]
            total["count"] += row["count"]
            total["unrecorded"] |= row["unrecorded"]
            for f in FIELDS:
                total[f] += row[f]
    for scope, total in sorted(totals.items(), key=lambda t: (t[0] == "All sources", t[0])):
        lines.append(f"| **{scope}** | | | | {total['count']} | "
                     + " | ".join(cell(total, f) for f in FIELDS) + f" | {total['input'] + total['output']:,} |")
    return "\n".join(lines)


def report(args):
    project = Path(args.project).resolve()
    orchestration = project / ".orchestration"
    ledger = Ledger(parse_time(args.since), parse_time(args.until))
    sessions = defaultdict(list)
    for period in (read_json(sessions_file(project)) or {}).get("sessions", []):
        sessions[period["id"]].append((parse_time(period.get("from")), parse_time(period.get("until"))))
    whole = {s: None for s in args.claude_session}
    if not sessions and not whole:
        ledger.missing.append("Claude: no session registered (run `token_ledger.py register`), "
                              "none given with --claude-session")
    add_claude(ledger, {**sessions, **whole})
    if orchestration.is_dir():
        add_codex(ledger, orchestration)
        add_vm(ledger, orchestration)
    else:
        ledger.missing.append(f"no {orchestration}: no Codex or VM worker counted")
    if args.json:
        print(json.dumps({"project": str(project), "observed_at": now(),
                          "rows": [{"source": k[0], "agent": k[1], "model": k[2], "effort": k[3],
                                    "count": r["count"],
                                    **{f: (None if f in r["unrecorded"] and r[f] == 0 else r[f]) for f in FIELDS},
                                    "partial": sorted(f for f in r["unrecorded"] if r[f])}
                                   for k, r in sorted(ledger.rows.items(), key=lambda i: tuple(map(str, i[0])))],
                          "not_counted": ledger.missing}, indent=1))
        return 0
    print(f"Token use for {project}, counted {now()}.\n")
    print("Count: sessions for the coordinator, subagents, Codex attempts, or VM runs (once per effort "
          "they used). Input tokens "
          "include cached ones and output tokens include reasoning ones; Total is input plus output.\n")
    print(table(ledger) if ledger.rows else "No token use found.")
    if ledger.missing:
        print("\nNot counted or incomplete:\n")
        for item in ledger.missing:
            print(f"- {item}")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="action", required=True)
    r = sub.add_parser("register", help="count the current Claude Code session from now on")
    r.add_argument("--project", required=True, help="project root (holds .orchestration/)")
    r.add_argument("--session", help="session id (default: CLAUDE_CODE_SESSION_ID)")
    r.add_argument("--end", action="store_true", help="stop counting this session from now on")
    p = sub.add_parser("report", help="print the tokens per agent, model and effort")
    p.add_argument("--project", required=True, help="project root (holds .orchestration/)")
    p.add_argument("--claude-session", action="append", default=[], metavar="ID",
                   help="also count this Claude Code session whole (for a campaign without registration)")
    p.add_argument("--since", help="count only what started at or after this ISO time")
    p.add_argument("--until", help="count only what started at or before this ISO time")
    p.add_argument("--json", action="store_true")
    args = parser.parse_args()
    return {"register": register, "report": report}[args.action](args)


if __name__ == "__main__":
    sys.exit(main())
