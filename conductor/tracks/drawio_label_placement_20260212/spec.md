# Track Spec: Draw.io Smart Label Placement & Tunnel Endpoint Octets

## Problem Statement

Two visual deficiencies were identified in generated topology diagrams:

1. **Device label always placed LEFT** — `generate_topo.py` hard-codes the label box to the
   left of every device icon. When a device (e.g. R2) has all its physical connections exiting
   from the LEFT side, the label overlaps those links and becomes unreadable. The label should
   be placed on whichever side is free of connections.

2. **Tunnel endpoint octets missing** — Tunnel overlay arcs (GRE, IPsec, etc.) exit from the
   top-center of each device, but no `.1` / `.2` last-octet labels are rendered near those
   exit points, making it hard to identify which IP belongs to each tunnel endpoint.

## Root Cause

- `generate_xml()` always sets `label_x = x - 100` regardless of where connections exit.
- `generate_tunnel_xml()` emits the arc and its edge label but no per-endpoint octet labels.

## Scope

- Update **SKILL.md** Sections 4.3 and 4.9 to document the corrected rules.
- Update **generate_topo.py** to implement both fixes.
- **Do NOT** re-generate any existing topology.drawio files.

## Acceptance Criteria

- [ ] SKILL.md Section 4.3 documents the "empty side" label placement rule.
- [ ] SKILL.md Section 4.9 documents tunnel endpoint octet placement.
- [ ] `generate_topo.py` has a `get_label_side()` function.
- [ ] `generate_xml()` uses `get_label_side()` per device.
- [ ] `generate_tunnel_xml()` emits `.1` / `.2` octet labels near tunnel arc endpoints.
- [ ] No existing topology.drawio files are modified.
