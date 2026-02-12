# Track Plan: Draw.io Smart Label Placement & Tunnel Endpoint Octets

## Tasks

- [x] **Update SKILL.md Section 4.3** — Replace "always LEFT" rule with smart placement rule:
  assess which side of the device has no connections and place the label there.

- [x] **Update SKILL.md Section 4.9** — Add rule for tunnel endpoint octet labels:
  `.1` near top of tunnel source device, `.2` near top of tunnel target device.

- [x] **Add `get_label_side()` to generate_topo.py** — Checks all physical neighbors;
  if all are to the LEFT → return `'right'`; if all to the RIGHT → return `'left'`;
  otherwise → default `'left'`.

- [x] **Update `generate_xml()`** — Call `get_label_side()` per device; adjust
  `label_x` accordingly (LEFT: `x - 105`, RIGHT: `x + 83`).

- [x] **Update `generate_tunnel_xml()`** — After the arc cells, emit two additional
  `mxCell` octet labels: `.1` at `(sx+44, sy-15)` and `.2` at `(dx+44, dy-15)`.

- [x] **Add track to conductor/tracks.md**
