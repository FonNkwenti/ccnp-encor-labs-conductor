---
name: drawio
description: Standards and workflows for creating and managing network diagrams using Draw.io.
---

# Draw.io Diagram Skill

## 1. Locations

Store diagrams in the following directories based on their type:

- **Topology Diagrams**: `labs/[chapter]/[lab-folder]/topology.drawio`
  - Use for network topologies, physical cabling, and logical connectivity.
- **Flow Diagrams**: `labs/[chapter]/[lab-folder]/flow-[description].drawio`
  - Use for packet flows, process charts, and logic flows.

## 2. File Formats

For every diagram, you must maintain two files with the **exact same basename**:

1.  **Source File (`.drawio`)**: The editable XML format.
2.  **Exported Image (`.png`)**: The visual representation for documentation.
    - *Note:* When exporting to PNG, ensure "Include path" or "copy of my drive" options are unselected if using the web version, but for local usage, a standard transparent background PNG is preferred.

## 3. Naming Conventions

- Use **kebab-case** for all filenames.
- **Pattern**: `[lab-name]-[diagram-type].extension`
- **Examples**:
  - `eigrp-basic-adjacency-topology.drawio`
  - `eigrp-basic-adjacency-topology.png`
  - `packet-flow-vlan-routing.drawio`

## 4. Design Standards

- **Icons**: Use official Cisco Network Topology Icons.
  - **Technical Implementation**: When generating XML, use the following `style` strings:
    - **Router**: `shape=mxgraph.cisco.routers.router;fillColor=#036897;strokeColor=#ffffff;`
    - **L3 Switch**: `shape=mxgraph.cisco.switches.layer_3_switch;fillColor=#036897;strokeColor=#ffffff;`
    - **L2 Switch**: `shape=mxgraph.cisco.switches.workgroup_switch;fillColor=#036897;strokeColor=#ffffff;`
    - **Cloud/Internet**: `shape=mxgraph.cisco.misc.cloud;fillColor=#036897;strokeColor=#ffffff;`
- **Colors**:
  - **Routers**: Blue (`#036897`).
  - **Annotation Boxes**: Light Yellow (`#fff2cc`) with Gold border (`#d6b656`).
- **Labels**:
  - Include Hostname, Interface Name (e.g., Gi0/0), and IP Address/Subnet.
  - Use 11pt bold for hostnames, 10pt for interface details.

## 5. Workflow

### Creating a New Diagram
1.  Open Draw.io (Desktop or Web).
2.  Create the diagram following design standards.
3.  Save the editable file as `.drawio` in the appropriate `assets/` subdirectory.
4.  Export the diagram as a `.png` (Transparent Background, 200% Zoom/Scale 2.0 for high DPI) to the same directory.
5.  Link the PNG in your README.md files: `![Topology](../../assets/diagrams/topology-diagrams/my-lab-topology.png)`

### Updating a Diagram
1.  Open the existing `.drawio` file.
2.  Make necessary modifications.
3.  Save the `.drawio` file.
4.  Re-export to `.png`, overwriting the existing image.
