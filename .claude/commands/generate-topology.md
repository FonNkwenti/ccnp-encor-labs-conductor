Generate or update a Draw.io topology diagram for: $ARGUMENTS

## Standards
Follow the full visual style guide at `.agent/skills/drawio/SKILL.md`. Key rules:

### Canvas & Layout
- Title at top center, bold, 16pt
- Legend box at bottom-right: black fill `#000000`, white text `#FFFFFF`, rounded corners, 10pt

### Device Icons
- Use Cisco shapes from `mxgraph.cisco` library
- Router: `shape=mxgraph.cisco.routers.router;fillColor=#036897;strokeColor=#ffffff;strokeWidth=2;`
- L3 Switch: `shape=mxgraph.cisco.switches.layer_3_switch;fillColor=#036897;strokeColor=#ffffff;strokeWidth=2;`

### Device Labels (Smart Placement)
- Three lines: hostname, role, loopback IP (e.g., `R1\nHub/ABR\n10.1.1.1/32`)
- Place on the "empty side" — the side with NO connection lines:
  - All neighbors LEFT → label RIGHT (`device_x + 83`)
  - All neighbors RIGHT → label LEFT (`device_x - 105`)
  - Mixed → default LEFT

### Connection Lines
- **White** (`#FFFFFF`), `strokeWidth=2`. Never black.
- Edge labels: interface pair + subnet (e.g., `Fa1/0 - Fa0/0\n10.12.0.0/30`)

### IP Last Octet Labels
- Every interface endpoint gets a `.1`, `.2` label near the router side
- Style: `edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];fontSize=10;`

### Layout — No Link Crossthrough
- If a bypass link connects non-adjacent devices in a vertical chain, offset intermediate devices horizontally by ~100px to create a triangle layout

### Tunnel Overlays
- Thin (`strokeWidth=1`), dashed (`dashed=1;dashPattern=1 4;`), curved above devices
- Color-coded: GRE=white `#FFFFFF`, MPLS=orange `#FF6600`, IPsec=red `#FF0000`, VXLAN=cyan `#00AAFF`, L2TP=purple `#AA00FF`
- Arc waypoints: `arc_y = min(source_y, target_y) - 100`

## Workflow
1. Read the chapter's `baseline.yaml` for device positions, links, and IPs
2. Generate the `.drawio` XML following all style rules above
3. Run validation checklist from `.agent/skills/drawio/SKILL.md` Section 5
4. Export to PNG: `python3 labs/common/tools/export_diagrams.py --file <path>`
