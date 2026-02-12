# Track Plan: Fault Injection Scripts — Hide Commands from Student Terminal Output

## Tasks

- [ ] **Update `fault_utils.py`** — Remove `print(f"  Executing: {cmd}")` on line 28.
  Remove or silence `print(f"[{description}] Connecting to {self.host}:{port}...")` on line 13.
  Remove `print(f"  Successfully executed commands.")` on line 35.
  Keep the error print on line 38.

- [ ] **Update Lab 01 scripts** — `labs/eigrp/lab-01-basic-adjacency/scripts/fault_inject_{1,2,3}.py`:
  Replace all print statements with generic challenge-number-only output.
  Change `description` arg in `execute_commands()` to `"Challenge N"`.

- [ ] **Update Lab 02 scripts** — `labs/eigrp/lab-02-path-selection/scripts/fault_inject_{1,2,3}.py`:
  Same pattern as Lab 01.

- [ ] **Update Lab 03 scripts** — `labs/eigrp/lab-03-route-summarization/scripts/fault_inject_{1,2,3}.py`:
  Same pattern as Lab 01.

- [ ] **Update Lab 04 scripts** — `labs/eigrp/lab-04-stub-wan-opt/scripts/fault_inject_{1,2,3}.py`:
  Same pattern as Lab 01.

- [ ] **Update Lab 05 scripts** — `labs/eigrp/lab-05-authentication-advanced/scripts/fault_inject_{1,2,3}.py`:
  Same pattern as Lab 01.

- [ ] **Update Lab 06 scripts** — `labs/eigrp/lab-06-filtering-control/scripts/fault_inject_{1,2,3}.py`:
  Same pattern as Lab 01.

- [ ] **Update Lab 07 scripts** — `labs/eigrp/lab-07-redistribution/scripts/fault_inject_{1,2,3}.py`:
  Same pattern as Lab 01.

- [ ] **Update Lab 08 scripts** — `labs/eigrp/lab-08-eigrp-over-vpn/scripts/fault_inject_{1,2,3}.py`:
  Same pattern as Lab 01.

- [ ] **Update Lab 09 scripts** — `labs/eigrp/lab-09-dual-stack-migration/scripts/fault_inject_{1,2,3}.py`:
  Same pattern as Lab 01.

- [ ] **Add track to `conductor/tracks.md`**

## Reference: Before/After Pattern

### `fault_utils.py` — BEFORE

```python
def execute_commands(self, port, commands, description="Injecting fault"):
    print(f"[{description}] Connecting to {self.host}:{port}...")
    ...
    for cmd in commands:
        print(f"  Executing: {cmd}")
        tn.sendall(cmd.encode('ascii') + b"\n")
        time.sleep(0.2)
    ...
    print(f"  Successfully executed commands.")
```

### `fault_utils.py` — AFTER

```python
def execute_commands(self, port, commands, description="Injecting fault"):
    try:
        tn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tn.settimeout(5)
        tn.connect((self.host, port))
        ...
        for cmd in commands:
            tn.sendall(cmd.encode('ascii') + b"\n")
            time.sleep(0.2)
        ...
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False
```

### `fault_inject_*.py` — BEFORE (example: Lab 01 Challenge 1)

```python
def inject():
    """AS Number Mismatch on R2"""
    print("Injecting Challenge 1: AS Number Mismatch...")
    commands = [...]
    injector = FaultInjector()
    injector.execute_commands(5002, commands, "R2 AS Mismatch")
    print("\nChallenge 1 injected successfully.")
```

### `fault_inject_*.py` — AFTER (example: Lab 01 Challenge 1)

```python
def inject():
    """AS Number Mismatch on R2"""
    commands = [...]
    injector = FaultInjector()
    injector.execute_commands(5002, commands, "Challenge 1")
    print("\nChallenge 1 fault injected successfully.")
    print("Refer to challenges.md for the symptom and goal.")
```
