# Track: Draw.io Smart Label Placement & Tunnel Endpoint Octets

**Status**: Complete
**Date**: 2026-02-12

## Summary

Fixed two visual deficiencies in the Draw.io topology generator:

1. **Smart label placement** — Device labels are now placed on the side with no connections.
   If all physical neighbors are to the LEFT, the label goes RIGHT (and vice versa).
   This prevents labels from overlapping link lines.

2. **Tunnel endpoint octets** — Tunnel arcs now show `.1` and `.2` octet labels near the
   top of the source and target devices respectively, matching the style used on physical links.

## Files Changed

- `.agent/skills/drawio/SKILL.md` — Sections 4.3 and 4.9 updated.
- `.agent/skills/drawio/scripts/generate_topo.py` — `get_label_side()` added,
  `generate_xml()` and `generate_tunnel_xml()` updated.
