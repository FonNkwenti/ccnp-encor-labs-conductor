# Track: Fault Injection Scripts — Hide Commands from Student Terminal Output

**Status**: Pending
**Date**: 2026-02-12

## Summary

The fault injection scripts currently log every IOS command to the terminal when a student
runs them, which reveals the answer to the troubleshooting challenge. This track fixes all 27
EIGRP fault scripts and the shared `fault_utils.py` utility so that the only terminal output
is a generic confirmation (e.g. "Challenge 1 fault injected successfully.") with a pointer to
`challenges.md`.

## Files Changed

- `labs/common/tools/fault_utils.py` — Remove command-level and description logging.
- `labs/eigrp/lab-{01..09}/scripts/fault_inject_{1,2,3}.py` (27 files) — Genericize prints.
