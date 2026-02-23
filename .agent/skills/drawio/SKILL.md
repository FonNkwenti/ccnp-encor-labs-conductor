---
name: drawio
description: Applies the CCNP lab topology diagram visual standard to Draw.io XML files: Cisco mxgraph icons (blue fill), white stroke connections, IP last-octet labels, smart label placement (empty-side rule), tunnel arcs with color coding, and black/white legend boxes. Use when asked to "create a topology diagram", "update topology.drawio", "draw the network", "generate the diagram", "fix the topology", or when a lab's topology.drawio needs to be created or updated. See references/drawio-xml-snippets.md for ready-to-paste XML.
metadata:
  author: CCNP ENCOR Labs Conductor
  version: 2.0.0
  category: document-creation
  tags: [drawio, cisco, topology, network-diagram, gns3, xml, ccnp]
---

# Draw.io Diagram Skill

## 1. Locations

Store diagrams in the following directories based on their type:

- **Topology Diagrams**: `labs/[chapter]/[lab-folder]/topology.drawio`
  - Use for network topologies, physical cabling, and logical connectivity.
- **Flow Diagrams**: `labs/[chapter]/[lab-folder]/flow-[description].drawio`
  - Use for packet flows, process charts, and logic flows.

## 2. File Formats & Deliverables

For every diagram, you must maintain and deliver two files with the **exact same basename**:

1.  **Source File (`.drawio`)**: The editable XML format.
2.  **Exported Image (`.png`)**: A high-resolution visual representation for documentation.
    - **Scale**: 200% (Scale 2.0) for high DPI.
    - **Background**: Transparent.
    - **Quality**: Lossless.
    - **Automation**: Use `drawio-desktop` CLI or automated scripts when possible.

## 3. Naming Conventions

- Use **kebab-case** for all filenames.
- **Pattern**: `[lab-name]-[diagram-type].extension`
- **Examples**:
  - `eigrp-basic-adjacency-topology.drawio`
  - `eigrp-basic-adjacency-topology.png`
  - `packet-flow-vlan-routing.drawio`

## 4. Visual Style Guide

This section defines the canonical visual style for all topology diagrams. Every generated `.drawio` file **must** follow these rules.

### 4.1 Canvas & Layout

- **Background**: Default Draw.io canvas (assumed dark-theme friendly).
- **Title**: Positioned at the **top center** of the canvas. Bold, 16pt.
- **Legend Box**: Required in every diagram. Positioned at the **bottom-right** corner. Black fill (`#000000`) with white text (`#FFFFFF`), rounded corners, 10pt font.

### 4.2 Device Icons

- Use official **Cisco Network Topology Icons** from the `mxgraph.cisco` shape library.
- **Style Strings**:
  - **Router**: `shape=mxgraph.cisco.routers.router;fillColor=#036897;strokeColor=#ffffff;strokeWidth=2;verticalLabelPosition=bottom;verticalAlign=top;align=center;outlineConnect=0;`
  - **L3 Switch**: `shape=mxgraph.cisco.switches.layer_3_switch;fillColor=#036897;strokeColor=#ffffff;strokeWidth=2;`
  - **L2 Switch**: `shape=mxgraph.cisco.switches.workgroup_switch;fillColor=#036897;strokeColor=#ffffff;strokeWidth=2;`
  - **Cloud/Internet**: `shape=mxgraph.cisco.misc.cloud;fillColor=#036897;strokeColor=#ffffff;strokeWidth=2;`

### 4.3 Device Labels

- **Content**: Three lines — hostname, role, loopback IP.
- **Style**: `text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=top;whiteSpace=wrap;rounded=0;fontSize=11;fontStyle=1`
- **Example**: `R1\nHub/ABR\n10.1.1.1/32`

#### 4.3.1 Smart Label Placement — Empty Side Rule

Labels **must not overlap any connection lines**. Place the label on the side that has **no connections** exiting the device icon:

| Condition | Placement |
|-----------|-----------|
| All physical neighbors are to the **LEFT** (`nx < device_x`) | Place label **RIGHT**: `label_x = device_x + 83` |
| All physical neighbors are to the **RIGHT** (`nx > device_x`) | Place label **LEFT**: `label_x = device_x - 105` |
| Neighbors on both sides (or same-column only) | Default **LEFT**: `label_x = device_x - 105` |

- Y offset (all cases): `label_y = device_y - 7`
- Label width: `100`, height: `60`

**Examples from EIGRP Lab 08:**
- **R2** is at x=500. All neighbors (R1 at x=400, R3 at x=400) are to the LEFT → label goes **RIGHT** (`label_x = 583`).
- **R6** is at x=200. Its neighbor R1 is at x=400, which is to the RIGHT → label goes **LEFT** (`label_x = 95`).

### 4.4 Connection Lines

- **Color**: **White** (`#FFFFFF`). Never black.
- **Style String**: `endArrow=none;html=1;strokeWidth=2;strokeColor=#FFFFFF;fillColor=#f5f5f5;`
- **Dashed Links** (tunnels): `endArrow=none;html=1;strokeWidth=2;strokeColor=#FFFFFF;fillColor=#f5f5f5;dashed=1;`
- **Edge Labels** (interface names + subnet): Centered on the link. 10pt. Include interface pair and subnet on separate lines.
  - Example value: `Fa1/0 - Fa0/0\n10.12.0.0/30`

### 4.5 IP Last Octet Labels

- **Required**: Every router interface endpoint must have a small label showing the **last octet** of its IP address (e.g., `.1`, `.2`).
- **Position**: Near the router's side of the connection line, close to the interface.
  - Use the router's X + ~50px (to the right of the icon edge).
  - Y coordinate near the interface exit point on the router.
- **Style**: `edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];fontSize=10;`
- **Purpose**: Allows instant identification of which IP belongs to which router without reading the full subnet label.

### 4.6 Legend Box

Every diagram must include a legend box with the following properties:

- **Position**: Bottom-right area of the canvas.
- **Fill**: Black (`#000000`).
- **Font Color**: White (`#FFFFFF`).
- **Border**: Rounded, white stroke.
- **Style**: `rounded=1;whiteSpace=wrap;html=1;fillColor=#000000;strokeColor=#FFFFFF;fontColor=#FFFFFF;fontSize=10;align=left;verticalAlign=top;spacingLeft=8;spacingTop=8;`
- **Content**: Key information for reading the diagram:
  - OSPF Area designations (if applicable)
  - Link type indicators (solid = physical, dashed = tunnel)
  - Any cost or metric annotations
  - Protocol identifiers (OSPF Process ID, EIGRP AS, etc.)

### 4.8 Layout Rules — Avoiding Link Overlap

**Critical Rule**: A connection line must NEVER visually cross through an intermediate device. This happens when three or more devices share the same X coordinate in a vertical chain and a "bypass" link connects non-adjacent devices.

**Problem Pattern** (DO NOT USE when bypass links exist):
```
  R1 (400, 200)    ← bypass link R1→R3 draws a straight
  |                   vertical line through R2
  R2 (400, 400)
  |
  R3 (400, 600)
```

**Solution**: When a bypass link exists between two devices that have intermediate devices at the same X coordinate, **offset the intermediate device(s) horizontally** to create a triangle or staggered layout.

**Correct Pattern** — Offset R2 to create a clear triangle:
```
       R1 (400, 200)
      / \
     /   \              R1→R3 link has clear path on the left
    /     \
  R2 (500, 400)        R2 shifted right by ~100px
    \
     \
      R3 (400, 600)
```

**General Rules**:
1. **Detect bypass links**: Before placing devices, check if any link connects two devices that skip over intermediate devices in the vertical chain.
2. **Offset intermediate devices**: Shift the intermediate device(s) horizontally by at least 100px to create visual separation.
3. **Preferred offset direction**: Shift RIGHT (increase X) unless the right side is occupied by another device (R4, R7), in which case shift LEFT.
4. **Label adjustment**: When a device is offset, its label position must follow — labels go to the LEFT of the device icon, or ABOVE if the left side is crowded.
5. **Octet label adjustment**: IP last-octet labels must be repositioned to remain near their respective interface endpoints after any coordinate changes.

**When bypass links are NOT present** (pure linear chain R1→R2→R3 with no R1→R3 link), the standard vertical column layout at the same X is fine.

### 4.9 Overlay / Tunnel Lines

Tunnel overlays represent **logical connections** that run on top of the physical topology. They must be visually distinct from physical links.

#### 4.9.1–4.9.6 Tunnel XML, Colors, Arc Algorithm, Octet Labels, Legend & YAML

See `references/drawio-xml-snippets.md` for:
- Full style properties table
- Tunnel color reference (GRE=white, MPLS=orange, IPsec=red, VXLAN=cyan, L2TP=purple)
- Arc routing algorithm (`arc_y = min(src_y, tgt_y) - 100`, waypoints at `(x+39, arc_y)`)
- Ready-to-paste XML for tunnel arcs, endpoint octet labels, and legend format
- `baseline.yaml` `tunnel_overlays` schema

### 4.7 Reference XML Snippets

See `references/drawio-xml-snippets.md` for ready-to-paste XML for all elements:
- Title cell, router/switch icons
- Device labels (left and right placement)
- White connection lines with edge labels
- IP last-octet labels
- Legend box
- GRE/IPsec tunnel arcs with endpoint octet labels
- Bypass-link offset layout example

## 5. Workflow

### Creating a New Diagram
1.  Open Draw.io (Desktop or Web).
2.  Create the diagram following the Visual Style Guide (Section 4).
3.  **Validation Checklist**:
    - [ ] Title is at the top center, bold, 16pt.
    - [ ] All connection lines are **white** (`#FFFFFF`), strokeWidth=2.
    - [ ] Device labels are positioned on the **empty side** of the icon (no connection lines on that side). See Section 4.3.1.
    - [ ] Every device has a hostname, role, and Loopback IP.
    - [ ] Every link has interface names on BOTH ends.
    - [ ] Every interface has a **last octet** label (`.1`, `.2`) near the router.
    - [ ] Subnet ID is visible on every link (centered edge label).
    - [ ] **No link visually crosses through an intermediate device** (see Section 4.8).
    - [ ] **Tunnel overlays** use thin colored dotted lines and arc above physical devices (see Section 4.9).
    - [ ] **Tunnel endpoint octets** (`.1` / `.2`) are placed near the top of source/target devices (see Section 4.9.4).
    - [ ] Protocol boundaries (Areas, AS) are clearly marked.
    - [ ] **Legend box** is present (black fill, white text, bottom-right) and lists tunnel colors if tunnels are present.
4.  Save the editable file as `.drawio` in the appropriate subdirectory.
5.  Export the diagram as a `.png` (Transparent Background, 200% Zoom/Scale 2.0 for high DPI) to the same directory.
6.  Link the PNG in your README.md files.

### Updating a Diagram
1.  Open the existing `.drawio` file.
2.  Make necessary modifications.
3.  Validate against the checklist above.
4.  Save the `.drawio` file.
5.  Re-export to `.png`, overwriting the existing image.
