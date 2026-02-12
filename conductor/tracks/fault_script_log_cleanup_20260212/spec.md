# Track Spec: Fault Injection Scripts — Hide Commands from Student Terminal Output

## Problem Statement

When a student runs a fault injection script (e.g. `python3 scripts/fault_inject_1.py`), the
terminal output currently reveals **exactly which IOS commands were executed**, which spoils the
troubleshooting challenge. The student can simply read the terminal and know what was changed.

**Current problematic output (example from Lab 01, Challenge 1):**

```
Injecting Challenge 1: AS Number Mismatch...
[R2 AS Mismatch] Connecting to 127.0.0.1:5002...
  Executing: no router eigrp 100
  Executing: router eigrp 200
  Executing:  network 2.2.2.2 0.0.0.0
  Executing:  network 10.0.12.0 0.0.0.3
  Executing:  network 10.0.23.0 0.0.0.3
  Successfully executed commands.

Challenge 1 injected successfully.
```

There are two sources of leakage:

1. **`fault_utils.py` line 28** — `print(f"  Executing: {cmd}")` logs every command sent.
2. **Each `fault_inject_*.py` script** — The opening `print()` and the description parameter
   passed to `execute_commands()` reveal the nature of the fault (e.g. "AS Number Mismatch",
   "R2 AS Mismatch", "R3 SHA-256 -> MD5").

## Desired Behavior

After the fix, running a fault injection script should output something like:

```
Challenge 1 fault injected successfully.
Refer to challenges.md for the symptom and goal.
```

- **No IOS commands** should appear in the terminal.
- **No fault description** (like "AS Number Mismatch") should appear.
- The student only knows which challenge number was injected and is directed to `challenges.md`.

## Scope

### 1. `labs/common/tools/fault_utils.py`

- **Remove** line 28: `print(f"  Executing: {cmd}")`
- **Remove** or genericize the description from line 13: `print(f"[{description}] Connecting to {self.host}:{port}...")`.
  Replace with a silent connection (no print) or a generic message like `Connecting...`
  that does not include the description text.
- Keep the error print on line 38 (`print(f"  Error: {e}")`) — errors should still be visible.
- Remove `print(f"  Successfully executed commands.")` on line 35 — success is communicated
  by the calling script.

### 2. All 27 `fault_inject_*.py` scripts (EIGRP Labs 01–09, 3 per lab)

For every script, replace **all** print statements with exactly two lines of output:

```python
print(f"\nChallenge {N} fault injected successfully.")
print("Refer to challenges.md for the symptom and goal.")
```

Where `{N}` is the challenge number (1, 2, or 3), derived from the script filename.

**Remove:**
- The opening print that reveals the fault name (e.g. `print("Injecting Challenge 1: AS Number Mismatch...")`)
- The closing print that repeats the success (e.g. `print("\nChallenge 1 injected successfully.")`)

**Keep:**
- The docstring on the `inject()` function (it's not shown to the student).
- The `execute_commands()` call — but change the `description` parameter to a generic
  string like `f"Challenge {N}"` so the utility doesn't leak it either.

### Files to Modify (28 total)

| # | File | Change |
|---|------|--------|
| 1 | `labs/common/tools/fault_utils.py` | Remove command logging, genericize description print |
| 2–4 | `labs/eigrp/lab-01-basic-adjacency/scripts/fault_inject_{1,2,3}.py` | Genericize prints |
| 5–7 | `labs/eigrp/lab-02-path-selection/scripts/fault_inject_{1,2,3}.py` | Genericize prints |
| 8–10 | `labs/eigrp/lab-03-route-summarization/scripts/fault_inject_{1,2,3}.py` | Genericize prints |
| 11–13 | `labs/eigrp/lab-04-stub-wan-opt/scripts/fault_inject_{1,2,3}.py` | Genericize prints |
| 14–16 | `labs/eigrp/lab-05-authentication-advanced/scripts/fault_inject_{1,2,3}.py` | Genericize prints |
| 17–19 | `labs/eigrp/lab-06-filtering-control/scripts/fault_inject_{1,2,3}.py` | Genericize prints |
| 20–22 | `labs/eigrp/lab-07-redistribution/scripts/fault_inject_{1,2,3}.py` | Genericize prints |
| 23–25 | `labs/eigrp/lab-08-eigrp-over-vpn/scripts/fault_inject_{1,2,3}.py` | Genericize prints |
| 26–28 | `labs/eigrp/lab-09-dual-stack-migration/scripts/fault_inject_{1,2,3}.py` | Genericize prints |

## Acceptance Criteria

- [ ] `fault_utils.py` no longer prints individual commands or the description string.
- [ ] Every `fault_inject_*.py` only outputs the challenge number and a pointer to `challenges.md`.
- [ ] Docstrings inside `inject()` functions are preserved (they serve as code documentation).
- [ ] Error messages from failed connections are still visible.
- [ ] No functional changes to what commands are actually injected.
