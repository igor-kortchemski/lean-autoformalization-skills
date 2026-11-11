#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Launch, inspect and cancel one attempt of a Codex worker.

`launch` runs `codex exec` (or `codex exec resume`) in a fresh attempt
directory, in its own process session, with stdout as the JSONL event stream,
stderr in its own file, and the final message in `result.md`. It records the
process identity in `process.json`, writes `exit-status` atomically when the
worker ends, records in `settings.json` the model, effort and usage confirmed
from the Codex session log (for a resumed session, only the part this attempt
added), and exits with the worker's own code. With
`--max-minutes`, it stops the worker and its builds when the limit is reached
and exits with 124. `--cd` sets
the worker's working directory, such as its Git worktree; the attempt directory
can live elsewhere. `--provider openmathos` sends the model calls to Open Math
OS with the key in `OPENMATHOS_API_KEY`, or else in the macOS Keychain item of
that name, instead of the logged-in OpenAI account. With that provider the launcher
reads the team's weekly Open Math OS quota with `openmathos_quota.py` before
starting, and every `--quota-poll` minutes while the worker runs: it launches
nothing, or stops the worker and its builds, when less than `--floor-percent`
(5%) of the quota remains or when the quota cannot be read (three readings in a
row while running), and exits with 75. Without a provider, when an accounts file
lists several Codex accounts (see `codex_quota.py`), `--account auto` (the
default) runs the worker under the `CODEX_HOME` of the eligible account with the
most weighted headroom above its quota floors, and `--account NAME` under that
account if it is eligible; a resumed session stays on the account that holds it.
When no account qualifies it launches nothing and exits with 75. Run it in the
foreground of a background command so the coordinator is notified when it exits.

`status` reports whether an attempt is finished, running, interrupted (no
exit status and the recorded process gone) or unverified (it cannot be tied to
a live process: no process record, or a live process that is not provably the
recorded one).
`cancel` checks the process identity, then stops the worker's process group
and every descendant, including Lake and Lean builds, before returning; a
descendant stays tracked until it exits, even when its parent dies first. It
signals nothing it cannot attribute to the attempt. All three print JSON.
Exit codes: `launch` returns the worker's own code, 124 at the time limit, 75 at
a quota floor (Open Math OS, or every Codex account), 2 when a check before the start fails, and 126 or
127 when the Codex executable cannot run; `cancel` returns 0
when nothing of the attempt remains, 2 when processes survive, 3 when it cannot
verify the attempt. Standard library only.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time

SANDBOXES = ("read-only", "workspace-write", "danger-full-access")

# Other inference providers, defined on the command line so that the user's
# config.toml stays unchanged and --ignore-user-config still applies. The key
# is read by Codex from the named environment variable, never from a file.
PROVIDERS = {
    "openmathos": {
        "name": "Open Math OS",
        "base_url": "https://os.openmathmodel.org/v1",
        "env_key": "OPENMATHOS_API_KEY",
        "wire_api": "responses",
        "supports_websockets": False,
        "model_catalog_url": "https://os.openmathmodel.org/v1/models",
    },
}


def write_atomic(path, text):
    tmp = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    tmp.write_text(text)
    os.replace(tmp, path)


PS_ENV = {**os.environ, "LC_ALL": "C", "TZ": "UTC"}
LSTART = "%a %b %d %H:%M:%S %Y"


def ps(*args):
    # A fixed locale and time zone make start times comparable across runs.
    return subprocess.run(["ps", *args], capture_output=True, text=True, env=PS_ENV).stdout


def start_time(pid):
    return " ".join(ps("-o", "lstart=", "-p", str(pid)).split()) or None


def parse_start(text):
    try:
        return datetime.strptime(text, LSTART).replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None


def command_line(pid):
    return ps("-ww", "-o", "command=", "-p", str(pid)).strip() or None


def process_table():
    """Live processes: pid -> (ppid, pgid, start time, command name); zombies omitted."""
    table = {}
    for line in ps("-A", "-o", "pid=,ppid=,pgid=,stat=,lstart=,comm=").splitlines():
        parts = line.split(None, 9)
        if len(parts) < 10 or "Z" in parts[3]:
            continue
        table[int(parts[0])] = (int(parts[1]), int(parts[2]),
                                parse_start(" ".join(parts[4:9])), parts[9])
    return table


def tree(root, pgid, follow_root=True, window=None, table=None):
    """Processes in the worker's group, plus every descendant of the root.

    With a (not_before, not_after) window, keep only processes started inside it,
    so that a recycled group id or PID never selects an unrelated process.
    """
    table = process_table() if table is None else table

    def allowed(pid):
        if window is None:
            return True
        started = table[pid][2]
        return started is not None and window[0] <= started <= window[1]

    members = {pid for pid, row in table.items() if row[1] == pgid and allowed(pid)}
    frontier = ([root] if follow_root else []) + list(members)
    while frontier:
        parent = frontier.pop()
        for pid, row in table.items():
            if row[0] == parent and pid not in members and allowed(pid):
                members.add(pid)
                frontier.append(pid)
    members.discard(os.getpid())
    return {pid: table[pid][3] for pid in members if pid in table}


def signal_tree(pids, pgid, sig, whole_group=True):
    if whole_group:
        try:
            os.killpg(pgid, sig)
        except (ProcessLookupError, PermissionError):
            pass
    for pid in pids:
        try:
            os.kill(pid, sig)
        except (ProcessLookupError, PermissionError):
            pass


def stop_tree(root, pgid, grace, follow_root=True, window=None):
    """TERM the group and descendants, then KILL; return survivors.

    A process once found stays tracked, by its PID and start time, until it exits: when
    its parent dies first, it leaves the tree, but it must still be stopped."""
    whole_group = window is None
    known = {}

    def current():
        table = process_table()
        for pid in tree(root, pgid, follow_root, window, table):
            known.setdefault(pid, table[pid][2])
        return {pid: table[pid][3] for pid, started in known.items()
                if pid in table and table[pid][2] == started}

    live = current()
    deadline = time.monotonic() + grace
    while live and time.monotonic() < deadline:
        signal_tree(live, pgid, signal.SIGTERM, whole_group)
        time.sleep(0.5)
        live = current()
    if live:
        signal_tree(live, pgid, signal.SIGKILL, whole_group)
        time.sleep(1)
        live = current()
    return live


def next_attempt(task_dir):
    for _ in range(20):
        numbers = [int(m.group(1)) for p in task_dir.glob("attempt-*")
                   if (m := re.fullmatch(r"attempt-(\d+)", p.name))]
        attempt = task_dir / f"attempt-{max(numbers, default=0) + 1}"
        try:
            attempt.mkdir()
            return attempt
        except FileExistsError:
            continue  # another launch for the same task took this number
    raise RuntimeError(f"could not create a new attempt in {task_dir}")


def keychain_secret(service):
    """The macOS Keychain password stored under SERVICE for this user, or None."""
    try:
        found = subprocess.run(["security", "find-generic-password", "-a",
                                os.environ.get("USER", ""), "-s", service, "-w"],
                               capture_output=True, text=True)
    except OSError:
        return None
    return found.stdout.strip() if found.returncode == 0 else None


def fail(message, code=2, **extra):
    print(json.dumps({"error": message, **extra}))
    return code


QUOTA_FLOOR_EXIT = 75


def openmathos_remaining(timeout=20):
    """Percentage of the team's weekly Open Math OS quota that remains, or raise RuntimeError.

    Uses the bundled read-only `openmathos_quota.py`, which needs the Platform key."""
    script = Path(__file__).resolve().with_name("openmathos_quota.py")
    try:
        found = subprocess.run([sys.executable, "-I", str(script), "--json", "--timeout", str(timeout)],
                               capture_output=True, text=True, timeout=timeout * 3 + 10)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise RuntimeError(f"quota reading failed: {error}")
    if found.returncode != 0:
        raise RuntimeError(found.stderr.strip()[:200] or "quota reading failed")
    try:
        week = [w for w in json.loads(found.stdout)["windows"] if w.get("window") == "weekly"]
        return float(week[0]["remaining_percent_exact"])
    except (ValueError, KeyError, IndexError, TypeError):
        raise RuntimeError("the weekly quota window is missing or unreadable")


def codex_accounts(path, codex, timeout=20):
    """Every registered Codex account with its quota reading, and the one `codex_quota.py` chooses.

    Returns (None, None) when there is no accounts file; raises RuntimeError when it cannot be read."""
    if not Path(path).expanduser().is_file():
        return None, None
    script = Path(__file__).resolve().with_name("codex_quota.py")
    found = None
    try:
        found = subprocess.run([sys.executable, "-I", str(script), "--choose", "--json", "--codex", codex,
                                "--accounts", path, "--timeout", str(timeout)],
                               capture_output=True, text=True, timeout=timeout * 6 + 10)
        result = json.loads(found.stdout)
        return result["accounts"], result["chosen"]
    except (OSError, subprocess.TimeoutExpired, ValueError, KeyError, TypeError) as error:
        detail = (found and found.stderr.strip()[:200]) or str(error)
        raise RuntimeError(f"Codex accounts unreadable: {detail}")


def pick_account(args):
    """(account record or None, error message or None) for a launch without a provider."""
    try:
        accounts, chosen = codex_accounts(args.accounts, args.codex)
    except RuntimeError as error:
        return None, str(error)
    if accounts is None:
        return None, (None if args.account == "auto" else f"accounts file not found: {args.accounts}")
    by_name = {a["name"]: a for a in accounts}
    if args.resume:  # a session can only be resumed under the CODEX_HOME that holds its log
        holders = [a for a in accounts if session_log(args.resume, a["codex_home"])]
        if not holders:
            return None, f"session {args.resume} is in no registered account"
        if args.account not in ("auto", holders[0]["name"]):
            return None, f"session {args.resume} belongs to account {holders[0]['name']}"
        name = holders[0]["name"]
    else:
        name = chosen if args.account == "auto" else args.account
    account = by_name.get(name)
    if account is None:
        return None, ("no Codex account is above its quota floors" if name is None
                      else f"unknown account: {name}")
    if not account["eligible"]:
        return None, f"account {name} is below a quota floor, blocked or unreadable"
    return account, None


def build_command(args, attempt):
    cmd = [args.codex, "exec"]
    if args.resume:
        cmd.append("resume")
    cmd += ["--model", args.model, "-c", f'model_reasoning_effort="{args.effort}"',
            "--disable", "multi_agent", "--disable", "multi_agent_v2", "--json",
            "--output-last-message", str(attempt / "result.md")]
    if args.provider:
        cmd += ["-c", f'model_provider="{args.provider}"']
        for key, value in PROVIDERS[args.provider].items():
            cmd += ["-c", f"model_providers.{args.provider}.{key}={json.dumps(value)}"]
    if args.dangerously_bypass_approvals_and_sandbox:
        cmd.append("--dangerously-bypass-approvals-and-sandbox")
    elif args.resume:
        cmd += ["-c", f'sandbox_mode="{args.sandbox}"']
    else:
        cmd += ["--sandbox", args.sandbox]
    if args.skip_git_repo_check:
        cmd.append("--skip-git-repo-check")
    if args.ignore_user_config:
        cmd.append("--ignore-user-config")
    if args.resume:
        cmd.append(args.resume)
    cmd.append("-")
    return cmd


def session_log(thread, home=None):
    home = Path(home or os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    logs = sorted(home.glob(f"sessions/*/*/*/rollout-*{thread}.jsonl")) if thread else []
    return logs[-1] if logs else None


def session_settings(attempt, model, effort, resumed_from=None, home=None):
    """Model, effort and usage of an attempt, read from Codex's own records.

    Workers usually cannot tell which model and effort they ran with, and the
    JSONL events omit them; the Codex session log of the thread records both.
    For a resumed session, `resumed_from` is (log path, size at launch): only the
    lines this attempt added count, since earlier attempts may have used other settings.
    """
    info = {"requested": {"model": model, "effort": effort},
            "observed": {"model": [], "effort": []}, "usage": None, "usage_scope": None,
            "session_log": None}
    thread = None
    try:
        with open(attempt / "events.jsonl") as events:
            for line in events:
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(event, dict):
                    continue
                if event.get("type") == "thread.started" and thread is None:
                    thread = event.get("thread_id")
                elif event.get("type") == "turn.completed":
                    info["usage"] = event.get("usage")
                    info["usage_scope"] = "last turn of this attempt"
    except OSError:
        pass
    log_path = session_log(thread, home) or (Path(resumed_from[0]) if resumed_from else None)
    if log_path:
        info["session_log"] = str(log_path)
        offset = resumed_from[1] if resumed_from and resumed_from[0] == str(log_path) else 0
        if offset:
            info["session_log_from_byte"] = offset
        seen, total, before = info["observed"], [], []

        def walk(node, totals, seen):
            # `seen` is None in the lines before the attempt: only their totals count.
            if isinstance(node, dict):
                for key, value in node.items():
                    if key == "total_token_usage" and isinstance(value, dict):
                        totals.append(value)
                    elif seen is not None and key == "model" and isinstance(value, str):
                        if value not in seen["model"]:
                            seen["model"].append(value)
                    elif seen is not None and key in ("effort", "reasoning_effort") \
                            and isinstance(value, str):
                        if value not in seen["effort"]:
                            seen["effort"].append(value)
                    else:
                        walk(value, totals, seen)
            elif isinstance(node, list):
                for value in node:
                    walk(value, totals, seen)

        with open(log_path, "rb") as log:
            end = 0
            for line in log:
                start, end = end, end + len(line)
                cut = min(max(offset - start, 0), len(line))  # bytes of this line before the attempt
                for part, into, keep in ((line[:cut], before, None), (line[cut:], total, seen)):
                    try:
                        walk(json.loads(part), into, keep)
                    except json.JSONDecodeError:
                        continue
        if total:
            # Also present after a cancellation. A resumed session keeps counting, so
            # an attempt's own usage is the difference with the total before it started.
            info["usage"] = total[-1]
            info["usage_scope"] = "Codex session total when the attempt ended"
        if offset:
            info["usage_before_attempt"] = before[-1] if before else None
    observed = info["observed"]
    info["confirmed"] = observed["model"] == [model] and observed["effort"] == [effort]
    info["mismatch"] = bool(observed["model"] or observed["effort"]) and not info["confirmed"]
    return info


def launch(args):
    task_dir = Path(args.task_dir).resolve()
    brief = Path(args.brief).resolve() if args.brief else task_dir / "brief.md"
    workdir = Path(args.cd).resolve() if args.cd else Path.cwd()
    if not task_dir.is_dir():
        return fail(f"task directory not found: {task_dir}")
    if not workdir.is_dir():
        return fail(f"working directory not found: {workdir}")
    if not brief.is_file():
        return fail(f"brief not found: {brief}")
    env = None
    if args.provider:
        name = PROVIDERS[args.provider]["env_key"]
        if not os.environ.get(name):
            key = keychain_secret(name)
            if not key:
                return fail(f"{name} is neither set nor in the macOS Keychain "
                            f"for provider {args.provider}")
            env = {**os.environ, name: key}
    account = None
    if not args.provider:
        account, error = pick_account(args)
        if error:
            return fail(f"nothing launched: {error}", QUOTA_FLOOR_EXIT if "floor" in error else 2)
        if account:
            env = {**(env or os.environ), "CODEX_HOME": account["codex_home"]}
    quota = None
    if args.quota_poll <= 0:
        return fail("--quota-poll must be a positive number of minutes")
    if args.provider == "openmathos":
        try:
            left = openmathos_remaining()
        except RuntimeError as error:
            return fail(f"Open Math OS quota unknown, nothing launched: {error}", QUOTA_FLOOR_EXIT)
        if left < args.floor_percent:
            return fail(f"{left}% of the team's weekly Open Math OS quota remains, below the "
                        f"{args.floor_percent}% floor: nothing launched", QUOTA_FLOOR_EXIT,
                        weekly_remaining_percent=left)
        quota = {"floor_percent": args.floor_percent, "at_launch": left, "last": left, "stopped": None}
    try:
        attempt = next_attempt(task_dir)
    except RuntimeError as error:
        return fail(str(error))
    (attempt / "brief.md").write_text(brief.read_text())
    cmd = build_command(args, attempt)
    resumed_from = None
    home = account["codex_home"] if account else None
    if args.resume and (log_path := session_log(args.resume, home)):
        resumed_from = (str(log_path), log_path.stat().st_size)
    try:
        with open(attempt / "brief.md") as stdin, open(attempt / "events.jsonl", "w") as out, \
                open(attempt / "stderr.log", "w") as err:
            proc = subprocess.Popen(cmd, stdin=stdin, stdout=out, stderr=err, cwd=workdir, env=env,
                                    start_new_session=True)
    except OSError as error:
        code = 126 if isinstance(error, PermissionError) else 127
        write_atomic(attempt / "exit-status", f"{code}\n")
        print(json.dumps({"attempt_dir": str(attempt), "exit_code": code,
                          "error": str(error)}))
        return code
    record = {"attempt_dir": str(attempt), "pid": proc.pid, "pgid": proc.pid,
              "started": start_time(proc.pid), "launcher_pid": os.getpid(),
              "launched_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
              "workdir": str(workdir), "command": cmd}
    write_atomic(attempt / "process.json", json.dumps(record, indent=2) + "\n")

    def forward(signum, _frame):
        stop_tree(proc.pid, proc.pid, args.grace)

    for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(sig, forward)
    code, timed_out = 1, False
    deadline = time.monotonic() + 60 * args.max_minutes if args.max_minutes else None
    poll = 60 * args.quota_poll if quota else None
    next_check = time.monotonic() + poll if poll else None
    try:
        while True:
            limits = [t for t in (deadline, next_check) if t is not None]
            try:
                code = proc.wait(timeout=None if not limits
                                 else max(0.0, min(limits) - time.monotonic()))
                break
            except InterruptedError:
                continue
            except subprocess.TimeoutExpired:
                if deadline is not None and time.monotonic() >= deadline:
                    timed_out = True  # the time limit
                elif quota_ok(quota, args.floor_percent) or proc.poll() is not None:
                    # A worker that ended during the reading keeps its own exit code.
                    if proc.poll() is not None and quota["stopped"]:
                        quota["below_floor_after_exit"], quota["stopped"] = quota["stopped"], None
                    next_check = time.monotonic() + poll
                    continue
                # Stop the worker and its builds, as `cancel` does.
                stop_tree(proc.pid, proc.pid, args.grace)
                code = proc.wait()
                break
        code = (124 if timed_out else QUOTA_FLOOR_EXIT if quota and quota["stopped"]
                else (128 - code if code < 0 else code))
    finally:
        if proc.poll() is None:
            stop_tree(proc.pid, proc.pid, args.grace)
            code = proc.wait()
            code = 128 - code if code < 0 else code
        write_atomic(attempt / "exit-status", f"{code}\n")
    settings = session_settings(attempt, args.model, args.effort, resumed_from, home)
    settings["requested"]["provider"] = args.provider or "default"
    settings["requested"]["resume"] = args.resume or None
    if account:
        settings["codex_account"] = {"name": account["name"], "codex_home": account["codex_home"],
                                     "weight": account["weight"], "headroom": account["headroom"],
                                     "reading": account["reading"]}
    settings["requested"]["max_minutes"] = args.max_minutes or None
    settings["time_limit_reached"] = timed_out
    if quota:
        settings["openmathos_quota"] = quota
    write_atomic(attempt / "settings.json", json.dumps(settings, indent=2) + "\n")
    print(json.dumps({"attempt_dir": str(attempt), "exit_code": code,
                      "time_limit_reached": timed_out,
                      **({"quota_stop": quota["stopped"]} if quota and quota["stopped"] else {}),
                      "result": str(attempt / "result.md"),
                      "settings": {k: settings[k] for k in ("observed", "confirmed", "mismatch")}}))
    return code


def quota_ok(quota, floor):
    """Read the Open Math OS quota during a run; False when the worker must stop.

    Three unreadable readings in a row stop it, as a reading below the floor does."""
    try:
        quota["last"] = openmathos_remaining()
        quota["misses"] = 0
    except RuntimeError as error:
        quota["misses"] = quota.get("misses", 0) + 1
        if quota["misses"] >= 3:
            quota["stopped"] = f"quota unreadable 3 times in a row: {error}"
            return False
        return True
    if quota["last"] < floor:
        quota["stopped"] = f"{quota['last']}% of the weekly quota remains, below the {floor}% floor"
        return False
    return True


def attempt_dir(args):
    if args.attempt_dir:
        return Path(args.attempt_dir).resolve()
    task_dir = Path(args.task_dir).resolve()
    attempts = [p for p in task_dir.glob("attempt-*") if re.fullmatch(r"attempt-\d+", p.name)]
    if not attempts:
        return None
    return max(attempts, key=lambda p: int(p.name.split("-")[1]))


def inspect(attempt):
    """Return (record, state); record is None when process.json was never written."""
    status_file = attempt / "exit-status"
    record_file = attempt / "process.json"
    record = json.loads(record_file.read_text()) if record_file.exists() else None
    if status_file.exists():
        return record, {"state": "finished", "exit_code": int(status_file.read_text().strip())}
    if record is None:
        return None, {"state": "unverified",
                      "note": "no process record: the launch failed or was cut short; "
                              "check for a codex process of this attempt by hand"}
    pid = record["pid"]
    live_cmd = command_line(pid)
    ours = live_cmd is not None and "exec" in live_cmd and str(attempt) in live_cmd
    if ours and start_time(pid) == record["started"]:
        return record, {"state": "running"}
    if ours:
        return record, {"state": "unverified",
                        "note": "a process with this attempt's command is alive but its start "
                                "time differs from the record; nothing is signalled"}
    return record, {"state": "interrupted",
                    "note": "no exit-status and the recorded process is gone or reused"}


def leftover_window(attempt, record):
    """Start-time window of processes that may belong to a finished attempt."""
    began = parse_start(record.get("started"))
    if began is None:
        return None
    status_file = attempt / "exit-status"
    ended = (datetime.fromtimestamp(status_file.stat().st_mtime, timezone.utc)
             if status_file.exists() else datetime.now(timezone.utc))
    return (began, ended)


def leftovers(attempt, record, grace=None):
    """Find, or with a grace period stop, processes left by an attempt whose worker is gone."""
    if command_line(record["pgid"]) is not None:
        return {}  # the group id now belongs to a live leader: never touch it
    window = leftover_window(attempt, record)
    if window is None:
        return {}
    if grace is None:
        return tree(record["pid"], record["pgid"], follow_root=False, window=window)
    return stop_tree(record["pid"], record["pgid"], grace, follow_root=False, window=window)


def status(args):
    attempt = attempt_dir(args)
    if attempt is None:
        return fail("no attempt found")
    record, state = inspect(attempt)
    left = leftovers(attempt, record) if record and state["state"] in ("finished", "interrupted") else {}
    print(json.dumps({"attempt_dir": str(attempt), **state, "leftover_processes": left}))
    return 0


def cancel(args):
    attempt = attempt_dir(args)
    if attempt is None:
        return fail("no attempt found")
    record, state = inspect(attempt)
    if state["state"] == "unverified":
        print(json.dumps({"attempt_dir": str(attempt), "before": state["state"], **state,
                          "surviving_processes": None}))
        return 3
    if state["state"] == "running":
        survivors = stop_tree(record["pid"], record["pgid"], args.grace)
        deadline = time.monotonic() + args.grace
        while not (attempt / "exit-status").exists() and time.monotonic() < deadline:
            if command_line(record["launcher_pid"]) is None:
                break
            time.sleep(0.5)
    else:
        # The worker is gone: only processes of its group started during the
        # attempt can be traced; descendants that left the group cannot. Without
        # a process record (the launch failed), no process was started.
        survivors = leftovers(attempt, record, args.grace) if record else {}
    _, final = inspect(attempt)
    print(json.dumps({"attempt_dir": str(attempt), "before": state["state"], **final,
                      "surviving_processes": survivors}))
    return 0 if not survivors else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="action", required=True)

    run = sub.add_parser("launch", help="start one worker attempt and wait for it")
    run.add_argument("--task-dir", required=True)
    run.add_argument("--brief", help="brief file (default: TASK_DIR/brief.md)")
    run.add_argument("--cd", metavar="DIR",
                     help="worker's working directory, e.g. its worktree (default: current)")
    run.add_argument("--model", required=True)
    run.add_argument("--effort", required=True)
    run.add_argument("--sandbox", choices=SANDBOXES, default="workspace-write")
    run.add_argument("--provider", choices=sorted(PROVIDERS),
                     help="inference provider other than the logged-in OpenAI account")
    run.add_argument("--resume", metavar="SESSION_ID", help="continue an earlier session")
    run.add_argument("--account", default="auto",
                     help="Codex account of the accounts file, or auto (default) for the one with the "
                          "most weighted quota headroom; ignored with --provider")
    run.add_argument("--accounts", default="~/.config/lean-orchestrator/codex-accounts.json",
                     help="accounts file (default ~/.config/lean-orchestrator/codex-accounts.json); "
                          "without it, the default CODEX_HOME is used")
    run.add_argument("--skip-git-repo-check", action="store_true",
                     help="only for a non-Git project the user explicitly approved")
    run.add_argument("--ignore-user-config", action="store_true",
                     help="do not load the user's Codex config.toml")
    run.add_argument("--dangerously-bypass-approvals-and-sandbox", action="store_true",
                     help="'yolo' mode: only on the user's explicit choice")
    run.add_argument("--codex", default="codex", help="Codex CLI executable")
    run.add_argument("--grace", type=float, default=20)
    run.add_argument("--max-minutes", type=float, default=0,
                     help="stop the worker and its builds after this many minutes (0: no limit); "
                          "the launcher then exits with 124")
    run.add_argument("--floor-percent", type=float, default=5,
                     help="with --provider openmathos: share of the team's weekly quota left untouched "
                          "(lower it only on the user's instruction)")
    run.add_argument("--quota-poll", type=float, default=5,
                     help="with --provider openmathos: minutes between quota readings while the worker runs")

    for name, helptext in (("status", "report the state of an attempt"),
                           ("cancel", "stop an attempt and its builds")):
        p = sub.add_parser(name, help=helptext)
        where = p.add_mutually_exclusive_group(required=True)
        where.add_argument("--attempt-dir")
        where.add_argument("--task-dir", help="use its latest attempt")
        p.add_argument("--grace", type=float, default=20)

    args = parser.parse_args()
    return {"launch": launch, "status": status, "cancel": cancel}[args.action](args)


if __name__ == "__main__":
    sys.exit(main())
