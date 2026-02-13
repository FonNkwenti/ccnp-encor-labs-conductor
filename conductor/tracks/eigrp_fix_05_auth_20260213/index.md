# Track: Remove SHA-256 from EIGRP Lab 05 + Cascade Fix

**Status**: Complete
**Date**: 2026-02-13

## Summary

EIGRP Lab 05 had an objective asking students to configure HMAC-SHA-256 authentication between
R2 (c3725, IOS 12.4) and R3 (c3725, IOS 12.4). SHA-256 authentication is only available in
EIGRP Named Mode on IOS 15.x+, making this objective technically impossible on these platforms.
The broken SHA-256 config had also cascaded into Labs 06-09 initial-configs and solutions.

This track removes all SHA-256 references from Lab 05, cleans the cascade from Labs 06-09,
and updates chapter-level documentation. SHA-256 authentication is properly relocated to
Lab 10 (Named Mode), which targets the c7200 routers (R1, R6) running IOS 15.3.

## Files

- [Specification](./spec.md)
- [Implementation Plan](./plan.md)
- [Metadata](./metadata.json)
