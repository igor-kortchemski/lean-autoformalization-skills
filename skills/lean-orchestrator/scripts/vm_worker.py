#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Launch, follow, stop and collect one Open Math OS VM worker without the browser.

Unofficial and unsupported: not endorsed by Open Math OS, and it may break or be refused at any time.

`launch` creates a new project with model training off (and checks it), then opens the team VM's runtime and
does what the web app does for a new chat: `conversation.say` with the brief and the model settings, then
`conversation.ensure` and `sessions.create`. It refuses to launch when less than 5% of the team's weekly quota
remains (the floor) or the quota cannot be read, and when `--max-vm-workers` (4) runs launched by this script,
from any campaign of this user, are still running: each run holds a slot file in `--slots-dir` until it ends.
`wait` follows the run through `session_history` and interrupts it on its own input-token cap (set at launch),
a loop, a time limit, the quota floor, an unreadable quota or history, or any unexpected error. `wait` ends
with the turn: after a follow-up sent in the browser, run `wait --follow-up` at once, which waits for that
message and counts its caps from then; if that `wait` stops before the turn ends, run `wait` again, with or
without `--follow-up`, and it resumes. `stop` interrupts the run. `fetch` downloads the project's handoff/
folder and compares each file with the SHA-256 the agent printed, when it printed one. `status` prints one
line. `wait` and `status` save the run's own token counts in `RUN_DIR/usage.json`; everything else about a run
is kept in `RUN_DIR/run.json`.

The Platform key (`nuc_oc_…`) is read from OPENMATHOS_PLATFORM_KEY or the macOS Keychain item of that name and
is never printed, nor the runtime ticket. The runtime protocol is the web app's own and is not documented: the
script pins runtime 0.52.0 (IPC 6) and stops at once when the platform answers with another version; use the
browser route of the VM guide until the script is updated. Exit codes: 0 done (or, for `launch`, started),
2 time limit, 3 token or loop cap (run interrupted), 4 quota or history unreadable (`launch`: nothing
launched; `wait`: run interrupted), 5 runtime version changed, 6 a limit was reached but the interruption
failed (the run may still be spending: stop it), 7 quota floor (`launch`: nothing launched; `wait`: run
interrupted), 8 unexpected error in `wait` (run interrupted), 9 the cap on running VM workers (nothing
launched), 1 other errors; when `launch` fails after the brief was sent, it says so: the agent may be running.
`fetch` skips a listed file whose name is not a plain file name.
Standard library and curl only.
"""
import argparse
import base64
import fcntl
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import socket
import ssl
import struct
import subprocess
import sys
import time
import uuid
from pathlib import Path
from urllib.parse import quote

HOST = "os.openmathmodel.org"
BASE = f"https://{HOST}/v1"
KEY_NAME = "OPENMATHOS_PLATFORM_KEY"
RUNTIME, IPC, PROTOCOL = "0.52.0", 6, "agent-vm-runtime-v1"
SESSION_NAME = re.compile(r"^[a-z0-9][a-z0-9_.-]{0,63}$")


class Exit(RuntimeError):
    """An error with its own exit code (see above)."""

    def __init__(self, message, code):
        super().__init__(message)
        self.code = code


DEFAULT_MAX_INPUT_TOKENS = 20_000_000


def keychain_secret(service):
    try:
        found = subprocess.run(["security", "find-generic-password", "-a", os.environ.get("USER", ""),
                                "-s", service, "-w"], capture_output=True, text=True)
    except OSError:
        return None
    return found.stdout.strip() if found.returncode == 0 else None


def platform_key():
    key = os.environ.get(KEY_NAME) or keychain_secret(KEY_NAME)
    if not key:
        raise RuntimeError(f"no {KEY_NAME} in the environment or the Keychain")
    return key


def call(operation, body, timeout=60):
    """POST BODY to a Platform operation with curl; the authorization header goes through stdin."""
    found = subprocess.run(
        ["curl", "-sS", "-m", str(timeout), "-X", "POST", "-H", "@-", "-H", "Content-Type: application/json",
         "--data-binary", json.dumps(body), "-w", "\n%{http_code}", f"{BASE}/{operation}"],
        input=f"Authorization: Bearer {platform_key()}\n", capture_output=True, text=True)
    if found.returncode != 0:
        raise RuntimeError(f"{operation}: curl failed: {found.stderr.strip()[:200]}")
    text, _, status = found.stdout.rpartition("\n")
    if status != "200":
        raise RuntimeError(f"{operation} answered {status}: {text[:300]}")
    return json.loads(text)


def team_id(given):
    if given:
        return given
    orgs = call("orgs", {}).get("orgs", [])
    if len(orgs) != 1:
        raise RuntimeError(f"the key's owner has {len(orgs)} teams; pass --team")
    return orgs[0]["id"]


def weekly_remaining(team):
    """Percent of the team's weekly quota window that remains, or raise."""
    windows = call("org_model_usage", {"team": team}, timeout=30).get("windows", [])
    week = [w for w in windows if w.get("window") == "week"]
    try:
        spent, limit = float(week[0]["spent_usd"]), float(week[0]["limit_usd"])
    except (IndexError, KeyError, TypeError, ValueError):
        raise RuntimeError("the weekly quota window is missing or unreadable")
    if limit <= 0:
        raise RuntimeError("the weekly quota window reports no limit")
    return 100 * (1 - spent / limit)


def projects(team):
    rows, after = [], None
    while True:
        page = call("org_projects", {"team": team, "limit": 100, **({"after": after} if after else {})})
        rows += page.get("projects", [])
        after = page.get("next")
        if not after or not page.get("projects"):
            return rows


def history(team, project, session):
    records, after = [], None
    while True:
        body = {"team": team, "project": project, "session": session, "limit": 200}
        if after is not None:
            body["after"] = after
        page = call("session_history", body)
        records += page.get("records", [])
        after = page.get("next")
        if after is None or not page.get("records"):
            return records


# A minimal client for the runtime WebSocket: binary frames of newline-delimited JSON.
class Runtime:
    def __init__(self, team, wake=True):
        opened = call("open", {"team": team, "version": RUNTIME, "ipc_version": IPC, "wake": wake,
                               "ticket": True}, timeout=120)
        for _ in range(60):
            if opened.get("state") != "preparing":
                break
            time.sleep(2)
            opened = call("open", {"team": team, "version": RUNTIME, "ipc_version": IPC, "wake": wake,
                                   "ticket": True}, timeout=120)
        if opened.get("version") != RUNTIME or opened.get("ipc_version") != IPC:
            raise Exit(f"runtime changed: the platform runs runtime {opened.get('version')} / IPC "
                       f"{opened.get('ipc_version')}, not {RUNTIME} / {IPC}", 5)
        if opened.get("state") != "ready" or not opened.get("ticket"):
            raise RuntimeError(f"the VM is not ready: state {opened.get('state')}")
        path = f"/v1/runtime/{quote(opened['environment'])}?ticket={quote(opened['ticket'], safe='')}"
        cafile = "/etc/ssl/cert.pem" if os.path.exists("/etc/ssl/cert.pem") else None
        raw = socket.create_connection((HOST, 443), timeout=60)
        self.sock = ssl.create_default_context(cafile=cafile).wrap_socket(raw, server_hostname=HOST)
        nonce = base64.b64encode(os.urandom(16)).decode()
        self.sock.sendall((f"GET {path} HTTP/1.1\r\nHost: {HOST}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
                           f"Sec-WebSocket-Key: {nonce}\r\nSec-WebSocket-Version: 13\r\n"
                           f"Sec-WebSocket-Protocol: {PROTOCOL}\r\n\r\n").encode())
        head = b""
        while b"\r\n\r\n" not in head:
            head += self._exact(1)
        lines = head.decode(errors="replace").split("\r\n")
        if " 101 " not in lines[0] or not any(l.lower() == f"sec-websocket-protocol: {PROTOCOL}"
                                              for l in lines):
            raise Exit(f"runtime changed: handshake refused: {lines[0]}", 5)
        self.buffer, self.next_id = b"", 1
        self.write((json.dumps({"nucleus_key": platform_key()}) + "\n").encode())

    def _exact(self, n):
        data = b""
        while len(data) < n:
            chunk = self.sock.recv(n - len(data))
            if not chunk:
                raise RuntimeError("runtime connection closed")
            data += chunk
        return data

    def _send(self, payload, opcode=0x2):
        mask, n = os.urandom(4), len(payload)
        head = bytes([0x80 | opcode])
        if n < 126:
            head += bytes([0x80 | n])
        elif n < 65536:
            head += bytes([0x80 | 126]) + struct.pack(">H", n)
        else:
            head += bytes([0x80 | 127]) + struct.pack(">Q", n)
        self.sock.sendall(head + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(payload)))

    def _frame(self):
        b1, b2 = self._exact(2)
        opcode, n = b1 & 0x0F, b2 & 0x7F
        if n == 126:
            n = struct.unpack(">H", self._exact(2))[0]
        elif n == 127:
            n = struct.unpack(">Q", self._exact(8))[0]
        mask = self._exact(4) if b2 & 0x80 else None
        data = self._exact(n)
        return opcode, bytes(b ^ mask[i % 4] for i, b in enumerate(data)) if mask else data

    def write(self, line):
        # Like the web app: a long line goes out as several binary messages of at most 64 KiB.
        for start in range(0, len(line), 65536):
            self._send(line[start:start + 65536])

    def request(self, op, **fields):
        rid, self.next_id = self.next_id, self.next_id + 1
        self.write((json.dumps({"op": op, "id": rid, **fields}) + "\n").encode())
        while True:
            while b"\n" in self.buffer:
                line, self.buffer = self.buffer.split(b"\n", 1)
                try:
                    msg = json.loads(line)
                except ValueError:
                    continue
                if isinstance(msg, dict) and msg.get("id") == rid:
                    if "ok" in msg:
                        return msg["ok"]
                    error = msg.get("error") or {}
                    raise RuntimeError(f"{op}: {error.get('code')}: {error.get('message')}")
            opcode, data = self._frame()
            if opcode == 0x8:
                raise RuntimeError(f"runtime closed the connection during {op}")
            if opcode == 0x1:
                raise RuntimeError(f"runtime session ended during {op}: {data.decode(errors='replace')[:200]}")
            if opcode == 0x9:
                self._send(data, opcode=0xA)
            elif opcode in (0x0, 0x2):
                self.buffer += data

    def close(self):
        try:
            self._send(struct.pack(">H", 1000), opcode=0x8)
            self.sock.close()
        except OSError:
            pass


CHUNK = 262144  # the web app's upload and download chunk size


def download(rt, project, path):
    data, offset = b"", 0
    while True:
        reply = rt.request("files.download", dir=project, path=path, offset=offset)
        data += base64.b64decode(reply.get("data_base64", ""))
        if reply.get("next_offset") is None or reply["next_offset"] <= offset:
            return data
        offset = reply["next_offset"]


def upload(rt, project, local):
    """Upload a file to the project's folder in chunks, then download it and compare SHA-256."""
    data = Path(local).read_bytes()
    name, offset = Path(local).name, 0
    while True:
        chunk = data[offset:offset + CHUNK]
        rt.request("files.upload", dir=project, path=name, offset=offset,
                   data_base64=base64.b64encode(chunk).decode(), last=offset + len(chunk) >= len(data))
        offset += len(chunk)
        if offset >= len(data):
            break
    digest = hashlib.sha256(data).hexdigest()
    if hashlib.sha256(download(rt, project, name)).hexdigest() != digest:
        raise RuntimeError(f"upload of {name} did not round-trip: nothing was sent to the agent")
    return {"name": name, "bytes": len(data), "sha256": digest}


def load(run_dir):
    return json.loads((Path(run_dir) / "run.json").read_text())


def write_json(path, data):
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(json.dumps(data, indent=1) + "\n")
    os.replace(tmp, path)


def save(run_dir, record):
    """Write run.json, keeping alerts another command (such as `stop`) added meanwhile."""
    path = Path(run_dir) / "run.json"
    try:
        on_disk = json.loads(path.read_text()).get("alerts", [])
    except (OSError, ValueError):
        on_disk = []
    alerts = record.setdefault("alerts", [])
    alerts.extend(a for a in on_disk if a not in alerts)
    alerts.sort(key=lambda a: a.get("at", ""))
    write_json(path, record)


def stamp():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def release_slot(record):
    if record.get("slot"):
        try:
            Path(record["slot"]).unlink()
        except OSError:
            pass


def live_slots(slots_dir):
    """Slot files of runs still going; those of finished or vanished runs are removed."""
    live = []
    for slot in sorted(Path(slots_dir).expanduser().glob("*.json")):
        try:
            record = load(json.loads(slot.read_text())["run_dir"])
        except (OSError, ValueError, KeyError, TypeError):
            finished = True  # its slot file or run directory is gone or unreadable
        else:
            try:
                recs = history(record["team"], record["project"], record["session"])
                finished = bool(recs) and recs[-1].get("kind") in ("turn_complete", "interrupted")
            except Exception:
                finished = False  # unknown: count it
        if finished:
            slot.unlink(missing_ok=True)
        else:
            live.append(slot.name)
    return live


def launch(args):
    run_dir = Path(args.run_dir)
    if (run_dir / "run.json").exists():
        raise RuntimeError(f"{run_dir}/run.json exists: use a new run directory")
    if not SESSION_NAME.fullmatch(args.session):
        raise RuntimeError("chat names use a-z, 0-9, dot, dash and underscore, 64 characters at most")
    if args.max_input_tokens <= 0:
        raise RuntimeError("--max-input-tokens must be positive")
    brief = Path(args.brief).read_text()
    missing = [f for f in args.upload if not Path(f).is_file()]
    if missing:
        raise RuntimeError(f"files to upload not found: {missing}")
    team = team_id(args.team)
    if any(p.get("display_name") == args.display_name for p in projects(team)):
        raise RuntimeError(f"a project named {args.display_name!r} exists: choose a new name")
    for attempt in range(3):  # no launch without a quota reading
        try:
            left = weekly_remaining(team)
            break
        except RuntimeError as error:
            if attempt == 2:
                raise Exit(f"quota unreadable: {error}; nothing was launched", 4)
            time.sleep(15)
    if left < args.floor_percent:
        raise Exit(f"{left:.2f}% of the team's weekly quota remains, below the "
                   f"{args.floor_percent}% floor: nothing was launched", 7)
    slots = Path(args.slots_dir).expanduser()
    slots.mkdir(parents=True, exist_ok=True)
    with open(slots / ".lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)  # two launches never count the same free slot
        live = live_slots(slots)
        if len(live) >= args.max_vm_workers:
            raise Exit(f"{len(live)} VM workers launched by this script are still running "
                       f"(cap {args.max_vm_workers}): nothing was launched", 9)
        record = {"team": team, "display_name": args.display_name, "session": args.session,
                  "model": args.model, "effort": args.effort, "brief": str(Path(args.brief).resolve()),
                  "weekly_remaining_before": left, "max_input_tokens": args.max_input_tokens,
                  "floor_percent": args.floor_percent}
        run_dir.mkdir(parents=True, exist_ok=True)
        call("project_create", {"team": team, "display_name": args.display_name}, timeout=90)
        found = [p for p in projects(team) if p.get("display_name") == args.display_name]
        if len(found) != 1:
            raise RuntimeError(f"project {args.display_name!r} not found once after creation")
        record["project"] = found[0]["name"]
        record["slot"] = str(slots / f"{record['project']}.json")
        save(run_dir, record)  # before the slot file, which counts as finished without run.json
        write_json(Path(record["slot"]), {"run_dir": str(run_dir.resolve()), "at": stamp()})
    try:
        call("project_training", {"team": team, "project": record["project"], "training": False})
        check = [p for p in projects(team) if p.get("name") == record["project"]]
        if not check or check[0].get("training") is not False:
            raise RuntimeError("model training is not off for the new project: nothing was sent")
        scope = {"project": record["project"], "session": args.session}
        message_id = f"u-{uuid.uuid4()}"
        # The agent sees the project's folder at this path; a brief can name it as {PROJECT_REPO}.
        brief = brief.replace("{PROJECT_REPO}", f"/workspace/nucleus/work/projects/{record['project']}/repo")
        rt = Runtime(team)
        try:
            record["uploads"] = [upload(rt, record["project"], f) for f in args.upload]
            save(run_dir, record)
            past = rt.request("conversation.history", **scope, after_seq=None)
            if any(r.get("kind") == "user" for r in past.get("records", [])):
                raise RuntimeError("the chat already has a message: nothing was sent")
            rt.request("conversation.say", **scope, message_id=message_id, text=brief,
                       settings={"model": args.model, "reasoning_effort": args.effort})
            record.update(message_id=message_id, sent_at=stamp())
            save(run_dir, record)
            rt.request("conversation.ensure", **scope)
            rt.request("sessions.create", **scope, model=args.model, reasoning_effort=args.effort)
            record["started_at"] = stamp()
            save(run_dir, record)
        finally:
            rt.close()
    except Exception as error:
        if "sent_at" in record:
            # The brief went out: the agent may be running. Keep the slot; `wait` or `stop` frees it.
            raise RuntimeError(f"{error}; THE BRIEF WAS SENT: the agent may be running, follow it with "
                               f"`wait --run-dir {run_dir}` or interrupt it with `stop --run-dir {run_dir}`")
        release_slot(record)
        raise
    print(json.dumps({k: record[k] for k in ("project", "session", "model", "effort", "sent_at",
                                             "max_input_tokens")}))
    return 0


def interrupt(record):
    rt = Runtime(record["team"], wake=False)
    try:
        rt.request("sessions.interrupt", project=record["project"], session=record["session"])
    finally:
        rt.close()


def command(arguments):
    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments)
        except ValueError:
            return arguments
    if isinstance(arguments, dict):
        return str(arguments.get("command") or json.dumps(arguments))
    return json.dumps(arguments)


def state(record, loop, run_dir=None):
    recs = history(record["team"], record["project"], record["session"])
    if run_dir is not None:
        save_usage(run_dir, record, recs)
    last_user = max((i for i, r in enumerate(recs) if r.get("kind") == "user"), default=None)
    after = recs[last_user:] if last_user is not None else []
    done = bool(after) and after[-1].get("kind") in ("turn_complete", "interrupted")
    cmds = [command(r.get("arguments")) for r in after if r.get("kind") == "tool_call"]
    looping = len(cmds) >= loop and len(set(cmds[-loop:])) == 1
    # The run's own model use: the team quota also counts the team's other activity.
    calls = [r for r in recs if r.get("kind") == "model_call"]
    return {"records": len(recs), "done": done, "last_user": last_user,
            "interrupted": bool(after) and after[-1].get("kind") == "interrupted", "tool_calls": len(cmds),
            "model_calls": len(calls), "input_tokens": sum(r.get("input_tokens") or 0 for r in calls),
            "output_tokens": sum(r.get("output_tokens") or 0 for r in calls),
            "loop": cmds[-1][:80] if looping else None}


def save_usage(run_dir, record, recs):
    """Write the run's own model use, by effort, to RUN_DIR/usage.json.

    The VM records input tokens (cached or not, without a split) and output tokens per model call."""
    by_effort = {}
    for r in recs:
        if r.get("kind") == "model_call":
            row = by_effort.setdefault(r.get("reasoning_effort") or record.get("effort") or "unknown",
                                       {"model_calls": 0, "input_tokens": 0, "output_tokens": 0})
            row["model_calls"] += 1
            row["input_tokens"] += r.get("input_tokens") or 0
            row["output_tokens"] += r.get("output_tokens") or 0
    usage = {"model": record.get("model"), "by_effort": by_effort, "observed_at": stamp(),
             "complete": bool(recs) and recs[-1].get("kind") in ("turn_complete", "interrupted")}
    write_json(Path(run_dir) / "usage.json", usage)


def retry(read, attempts=3, pause=15):
    for attempt in range(attempts):
        try:
            return read()
        except Exception:
            if attempt == attempts - 1:
                raise
            time.sleep(pause)


def end_with_alert(run_dir, record, alert, code, st, finished=False):
    """Interrupt the run (unless it has finished), record the alert and return the exit code."""
    failure = None
    if not finished:
        try:
            interrupt(record)
        except Exception as error:
            failure, code = str(error)[:200], 6
    record.setdefault("alerts", []).append({"at": stamp(), "alert": alert, "interrupted": failure is None
                                            and not finished, **({"interrupt_error": failure} if failure else {})})
    if failure is None:
        release_slot(record)
    save(run_dir, record)
    if failure:
        print(f"{stamp()} ALERT {alert}; INTERRUPTION FAILED ({failure}): the run may still be "
              f"spending, stop it with `stop` or in the web app {json.dumps(st)}")
    elif finished:
        print(f"{stamp()} ALERT {alert}; the run's latest turn has finished, nothing to interrupt "
              f"{json.dumps(st)}")
    else:
        print(f"{stamp()} ALERT {alert}; run interrupted {json.dumps(st)}")
    return code


def wait(args):
    record = load(args.run_dir)
    if args.follow_up and not record.get("turns") and not record.get("awaiting_follow_up"):
        print("vm_worker: no earlier turn was followed by `wait`: run it without --follow-up", file=sys.stderr)
        return 1
    try:
        return follow(args, record)
    except Exception as error:  # never leave a run unwatched and running
        return end_with_alert(args.run_dir, record, f"unexpected error in wait: {type(error).__name__}: "
                              f"{str(error)[:200]}", 8, {})


def follow(args, record):
    max_tokens = args.max_input_tokens or record.get("max_input_tokens", DEFAULT_MAX_INPUT_TOKENS)
    floor = args.floor_percent if args.floor_percent is not None else record.get("floor_percent", 5)
    deadline = time.monotonic() + 60 * args.max_minutes
    turns = record.setdefault("turns", [])
    awaiting = record.get("awaiting_follow_up")
    if args.follow_up and awaiting is None:
        # The caps of a follow-up count from now: the earlier turns already spent their own.
        base = retry(lambda: {"input_tokens": state(record, args.loop)["input_tokens"]}, pause=args.poll)
        awaiting = record["awaiting_follow_up"] = {"after_user_index": turns[-1]["user_index"],
                                                   "since": stamp(), **base}
        save(args.run_dir, record)
    base = {"input_tokens": awaiting["input_tokens"] if awaiting else 0}
    turn, quota_misses, history_misses = None, 0, 0
    while True:
        try:
            st = state(record, args.loop, args.run_dir)
            history_misses = 0
        except Exception as error:
            st, history_misses = {"error": str(error)[:120]}, history_misses + 1
        user = st.get("last_user")
        if turn is None and user is not None:
            if awaiting is not None:
                if user > awaiting["after_user_index"]:  # the follow-up message has arrived
                    turn = {"user_index": user, "followed_from": awaiting["since"], **base}
                    turns.append(turn)
                    del record["awaiting_follow_up"]
                    awaiting = None
            elif turns and turns[-1]["user_index"] == user:
                turn = turns[-1]  # `wait` started again on the same turn
            else:
                turn = {"user_index": user, "followed_from": stamp(), **base}
                turns.append(turn)
            if turn is not None:
                save(args.run_dir, record)
        if turn is not None and st.get("done"):
            release_slot(record)
            save(args.run_dir, record)
            print(f"{stamp()} DONE {json.dumps(st)}")
            return 0
        try:
            left, quota_misses = weekly_remaining(record["team"]), 0
        except Exception:
            left, quota_misses = None, quota_misses + 1
        tokens = st.get("input_tokens", 0) - (turn or base)["input_tokens"]
        since = "since the follow-up" if turn is not None and turn.get("followed_from") and \
            len(turns) > 1 else "since launch"
        alert = None
        if history_misses >= 3:
            alert, code = "session history unreadable 3 times: the run cannot be followed", 4
        elif quota_misses >= 3:
            alert, code = "quota unreadable 3 times: budget unknown", 4
        elif left is not None and left < floor:
            alert, code = (f"quota floor: {left:.2f}% of the team's weekly quota remains (floor {floor}%); "
                           f"launch nothing more on Open Math OS until it is back above"), 7
        elif tokens > max_tokens:
            alert, code = f"budget: {tokens} input tokens {since} (cap {max_tokens})", 3
        elif turn is not None and st.get("loop"):
            alert, code = f"loop: last {args.loop} tool calls are all {st['loop']!r}", 3
        elif time.monotonic() > deadline:
            alert, code = (f"time limit of {args.max_minutes} minutes"
                           + ("; no follow-up message appeared" if awaiting is not None else "")), 2
        if alert:
            return end_with_alert(args.run_dir, record, alert, code, st,
                                  finished=turn is None and bool(st.get("done")))
        print(f"{stamp()} running {json.dumps(st)} tokens={tokens}/{max_tokens} "
              f"weekly_remaining={'?' if left is None else f'{left:.1f}%'}"
              + ("" if turn is not None else " (waiting for the follow-up message)"), flush=True)
        time.sleep(args.poll)


def stop(args):
    record = load(args.run_dir)
    interrupt(record)
    record.setdefault("alerts", []).append({"at": stamp(), "alert": "stopped by hand"})
    release_slot(record)
    save(args.run_dir, record)
    print("interrupted")
    return 0


def status(args):
    record = load(args.run_dir)
    st = state(record, args.loop, args.run_dir)
    try:
        left = round(weekly_remaining(record["team"]), 2)
    except Exception:
        left = None
    print(json.dumps({**st, "max_input_tokens": record.get("max_input_tokens", DEFAULT_MAX_INPUT_TOKENS),
                      "weekly_remaining_percent": left,
                      "awaiting_follow_up": "awaiting_follow_up" in record}))
    return 0


def tool_output(result):
    s = result.get("summary")
    if isinstance(s, str):
        try:
            s = json.loads(s)
        except ValueError:
            return s, False
    if isinstance(s, dict):
        output = s.get("output")
        return (output if isinstance(output, str) else ""), bool(s.get("truncated"))
    return ("" if s is None else str(s)), False


def fetch(args):
    """Download the files of the project's handoff/ folder and compare them with the SHA-256 the agent printed."""
    record = load(args.run_dir)
    recs = history(record["team"], record["project"], record["session"])
    printed = {}
    for r in recs:
        if r.get("kind") == "tool_result":
            for m in re.finditer(r"^([0-9a-f]{64})\s+\*?(\S+)$", tool_output(r)[0], re.M):
                name = os.path.basename(m.group(2))
                if name not in printed or "handoff/" in m.group(2):
                    printed[name] = m.group(1)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    rt = Runtime(record["team"], wake=False)
    try:
        listing = rt.request("files.list", dir=record["project"], path="handoff")
        names = [e["name"] for e in listing.get("entries", []) if e.get("kind") == "file"]
        report = {}
        for name in names:
            if (not isinstance(name, str) or name in ("", ".", "..") or "/" in name or "\\" in name
                    or (out_dir / name).is_symlink()):
                report[str(name)] = {"error": "unsafe file name, not downloaded", "match": False}
                continue
            data = download(rt, record["project"], f"handoff/{name}")
            target = out_dir / name
            target.write_bytes(data)
            digest = hashlib.sha256(data).hexdigest()
            report[name] = {"bytes": len(data), "sha256": digest, "printed_sha256": printed.get(name),
                            "match": None if name not in printed else printed[name] == digest}
    finally:
        rt.close()
    print(json.dumps(report, indent=1))
    return 0 if report and all(r["match"] is not False for r in report.values()) else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="action", required=True)
    p = sub.add_parser("launch", help="create a project with training off and start one chat")
    p.add_argument("--run-dir", required=True)
    p.add_argument("--display-name", required=True, help="new project name, unique in the team")
    p.add_argument("--session", required=True, help="chat name: a-z, 0-9, dot, dash, underscore")
    p.add_argument("--brief", required=True,
                   help="brief file; {PROJECT_REPO} becomes the agent's path to the new project's folder")
    p.add_argument("--upload", action="append", default=[], metavar="FILE",
                   help="file to upload to the project's folder before sending the brief (checked by SHA-256)")
    p.add_argument("--model", required=True, help="e.g. moonshotai/kimi-k3.1-pro")
    p.add_argument("--effort", required=True, help="e.g. high; Kimi accepts low, high and max")
    p.add_argument("--max-input-tokens", type=int, default=DEFAULT_MAX_INPUT_TOKENS,
                   help="the run's own input-token cap, kept for `wait` (default 20 million)")
    p.add_argument("--floor-percent", type=float, default=5,
                   help="share of the team's weekly quota left untouched (lower it only on the user's "
                        "instruction)")
    p.add_argument("--max-vm-workers", type=int, default=4,
                   help="cap on running VM workers launched by this script, across campaigns")
    p.add_argument("--slots-dir", default="~/.cache/lean-orchestrator/vm-slots",
                   help="where each running run holds its slot file (shared by all campaigns)")
    p.add_argument("--team")
    w = sub.add_parser("wait", help="follow the run; interrupt it on a limit")
    w.add_argument("--run-dir", required=True)
    w.add_argument("--max-minutes", type=float, default=40)
    w.add_argument("--max-input-tokens", type=int, default=0,
                   help="the run's own input-token cap (default: the launch's)")
    w.add_argument("--floor-percent", type=float,
                   help="interrupt when less than this share of the team's weekly quota remains "
                        "(default: the launch's floor)")
    w.add_argument("--loop", type=int, default=15, help="identical tool calls that count as a loop")
    w.add_argument("--poll", type=float, default=60)
    w.add_argument("--follow-up", action="store_true",
                   help="run right after sending a follow-up: wait for that message, then follow its "
                        "turn, with the caps counted from now")
    s = sub.add_parser("stop", help="interrupt the run")
    s.add_argument("--run-dir", required=True)
    t = sub.add_parser("status", help="one line about the run")
    t.add_argument("--run-dir", required=True)
    t.add_argument("--loop", type=int, default=15)
    f = sub.add_parser("fetch", help="download the handoff/ folder and check the printed SHA-256")
    f.add_argument("--run-dir", required=True)
    f.add_argument("--out", required=True)
    args = parser.parse_args()
    try:
        return {"launch": launch, "wait": wait, "stop": stop, "status": status, "fetch": fetch}[args.action](args)
    except Exit as error:
        print(f"vm_worker: {error}" + ("; use the browser route until vm_worker.py is updated"
                                       if error.code == 5 else ""), file=sys.stderr)
        return error.code
    except (OSError, RuntimeError, KeyError, ValueError) as error:
        print(f"vm_worker: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
