import sys
import os
import argparse
from datetime import datetime

# --- Simple YAML Parser (Subset for baseline.yaml) ---
def parse_simple_yaml(file_path):
    """
    A very basic YAML parser that handles the specific structure of baseline.yaml.
    It supports:
    - Top-level keys
    - Lists of dictionaries (indicated by "- ")
    - Dictionaries
    """
    with open(file_path, 'r') as f:
        lines = f.readlines()

    data = {
        'core_topology': {'devices': [], 'links': []},
        'optional_devices': [],
        'optional_links': [],
        'labs': [],
        'tunnel_overlays': [],
    }

    current_section = None
    current_list_item = None

    for line in lines:
        line = line.rstrip()
        if not line or line.strip().startswith('#'):
            continue

        indent = len(line) - len(line.lstrip())
        stripped = line.strip()

        # Top-level keys
        if indent == 0 and ':' in stripped:
            key = stripped.split(':')[0]
            if key in ['core_topology', 'optional_devices', 'optional_links', 'labs',
                       'tunnel_overlays']:
                current_section = key
                current_list_item = None
            continue

        # Sections
        if current_section == 'core_topology':
            if indent == 2 and stripped.startswith('devices:'):
                current_subsection = 'devices'
            elif indent == 2 and stripped.startswith('links:'):
                current_subsection = 'links'
            elif indent == 4 and stripped.startswith('- '):
                # New item in list
                item = {}
                key_val = stripped[2:].split(':', 1)
                if len(key_val) == 2:
                    item[key_val[0].strip()] = key_val[1].strip()
                current_list_item = item
                data['core_topology'][current_subsection].append(item)
            elif indent > 4 and current_list_item is not None and ':' in stripped:
                key, val = stripped.split(':', 1)
                current_list_item[key.strip()] = val.strip()

        elif current_section in ['optional_devices', 'optional_links', 'labs',
                                  'tunnel_overlays']:
            if indent == 2 and stripped.startswith('- '):
                item = {}
                key_val = stripped[2:].split(':', 1)
                if len(key_val) == 2:
                    item[key_val[0].strip()] = key_val[1].strip()
                current_list_item = item
                data[current_section].append(item)
            elif indent > 2 and current_list_item is not None and ':' in stripped:
                key, val = stripped.split(':', 1)

                # Special handling for list strings like [R1, R2]
                if val.strip().startswith('[') and val.strip().endswith(']'):
                    val = [x.strip() for x in val.strip()[1:-1].split(',')]
                else:
                    val = val.strip()

                current_list_item[key.strip()] = val

    return data

# --- Draw.io XML Templates ---
DRAWIO_HEADER = """<mxfile host="Electron" modified="{timestamp}" agent="generate_topo.py" etag="auto-gen" version="21.0.0">
  <diagram id="topology-diagram" name="Network Topology">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
"""

DRAWIO_FOOTER = """      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
"""

# --- Style Guide Compliant Styles ---
# See .agent/skills/drawio/SKILL.md Section 4 for full spec.
STYLE_ROUTER = "shape=mxgraph.cisco.routers.router;fillColor=#036897;strokeColor=#ffffff;strokeWidth=2;verticalLabelPosition=bottom;verticalAlign=top;align=center;outlineConnect=0;"
STYLE_LINK_SOLID = "endArrow=none;html=1;strokeWidth=2;strokeColor=#FFFFFF;fillColor=#f5f5f5;"
STYLE_LINK_DASHED = "endArrow=none;html=1;strokeWidth=2;strokeColor=#FFFFFF;fillColor=#f5f5f5;dashed=1;"
STYLE_CLOUD = "shape=mxgraph.cisco.misc.cloud;fillColor=#036897;strokeColor=#ffffff;strokeWidth=2;"
STYLE_DEVICE_LABEL = "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=top;whiteSpace=wrap;rounded=0;fontSize=11;fontStyle=1"
STYLE_OCTET_LABEL = "edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];fontSize=10;"
STYLE_LEGEND = "rounded=1;whiteSpace=wrap;html=1;fillColor=#000000;strokeColor=#FFFFFF;fontColor=#FFFFFF;fontSize=10;align=left;verticalAlign=top;spacingLeft=8;spacingTop=8;"

# Tunnel overlay colors by type (see SKILL.md Section 4.9)
TUNNEL_COLORS = {
    "gre":    "#FFFFFF",   # White
    "mpls":   "#FF6600",   # Orange
    "ipsec":  "#FF0000",   # Red
    "vxlan":  "#00AAFF",   # Cyan
    "l2tp":   "#AA00FF",   # Purple
}
TUNNEL_COLOR_DEFAULT = "#FFFF00"   # Yellow for unknown

TUNNEL_LEGEND_LABELS = {
    "gre":   "GRE",
    "mpls":  "MPLS",
    "ipsec": "IPsec VPN",
    "vxlan": "VXLAN",
    "l2tp":  "L2TP",
}


def get_tunnel_style(tunnel_type):
    """Return Draw.io edge style string for a tunnel overlay."""
    color = TUNNEL_COLORS.get(tunnel_type.lower(), TUNNEL_COLOR_DEFAULT)
    return (
        f"endArrow=none;html=1;strokeWidth=1;strokeColor={color};fillColor=none;"
        f"dashed=1;dashPattern=1 4;curved=1;"
        f"exitX=0.5;exitY=0;exitDx=0;exitDy=0;"
        f"entryX=0.5;entryY=0;entryDx=0;entryDy=0;"
    )


def generate_tunnel_xml(tunnel, tunnel_idx, coords):
    """Render a tunnel overlay as a curved arc above the physical topology."""
    src_dev = tunnel['source'].split(':')[0]
    dst_dev = tunnel['target'].split(':')[0]
    src_int = tunnel['source'].split(':')[1]
    dst_int = tunnel['target'].split(':')[1]
    subnet  = tunnel.get('subnet', 'N/A')
    ttype   = tunnel.get('type', 'gre').lower()

    sx, sy = coords.get(src_dev, (400, 200))
    dx, dy = coords.get(dst_dev, (200, 200))

    # Arc waypoints: curve above both devices
    arc_y  = min(sy, dy) - 100
    wp1_x  = sx + 39   # center of source icon
    wp2_x  = dx + 39   # center of target icon

    style  = get_tunnel_style(ttype)
    tid    = f"tunnel_{src_dev}_{dst_dev}_{tunnel_idx}"
    label  = f"{src_int} - {dst_int}&#10;{subnet}&#10;[{ttype.upper()}]"

    # Tunnel endpoint octet label positions (SKILL.md Section 4.9.4)
    # Place near the top of each device where the arc exits
    src_octet_x = sx + 44
    src_octet_y = sy - 15
    dst_octet_x = dx + 44
    dst_octet_y = dy - 15

    return f"""        <mxCell id="{tid}" value="" style="{style}" edge="1" parent="1" source="{src_dev}" target="{dst_dev}">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="{wp1_x}" y="{arc_y}"/>
              <mxPoint x="{wp2_x}" y="{arc_y}"/>
            </Array>
          </mxGeometry>
        </mxCell>
        <mxCell id="{tid}_lbl" value="{label}" style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];fontSize=10;" vertex="1" connectable="0" parent="{tid}">
          <mxGeometry relative="1" as="geometry"><mxPoint as="offset"/></mxGeometry>
        </mxCell>
        <mxCell id="{tid}_src_octet" value=".1" style="{STYLE_OCTET_LABEL}" vertex="1" connectable="0" parent="1">
          <mxGeometry x="{src_octet_x}" y="{src_octet_y}" as="geometry" />
        </mxCell>
        <mxCell id="{tid}_dst_octet" value=".2" style="{STYLE_OCTET_LABEL}" vertex="1" connectable="0" parent="1">
          <mxGeometry x="{dst_octet_x}" y="{dst_octet_y}" as="geometry" />
        </mxCell>
"""

# Base Coordinates for Standard Topology (Hub-and-Spoke + Add-ons)
BASE_COORDS = {
    "R1": (400, 200),  # Hub
    "R2": (400, 400),  # Branch
    "R3": (400, 600),  # Remote Branch
    "R4": (600, 200),  # OSPF Domain (Right of R1)
    "R5": (400, 800),  # Stub (Below R3)
    "R6": (200, 200),  # VPN Endpoint (Left of R1)
    "R7": (600, 400),  # Summary Boundary (Right of R2/Link from R1)
}

# Vertical chain devices (same X column) — used for bypass detection
VERTICAL_CHAIN = ["R1", "R2", "R3", "R5"]


def compute_coords(device_names, links):
    """Compute layout coordinates, offsetting intermediate devices when bypass
    links exist to prevent connection lines from visually crossing through
    devices.  See SKILL.md Section 4.8."""
    coords = {k: v for k, v in BASE_COORDS.items()}

    # Build set of link endpoints
    link_pairs = set()
    for link in links:
        src = link['source'].split(':')[0]
        dst = link['target'].split(':')[0]
        if src in device_names and dst in device_names:
            link_pairs.add((src, dst))
            link_pairs.add((dst, src))

    # Detect bypass links in the vertical chain.
    # A bypass exists when two chain devices are linked but have intermediate
    # chain devices between them (e.g., R1-R3 bypasses R2).
    chain_present = [d for d in VERTICAL_CHAIN if d in device_names]

    for i, src in enumerate(chain_present):
        for j in range(i + 2, len(chain_present)):
            dst = chain_present[j]
            if (src, dst) in link_pairs:
                # Bypass detected — offset all intermediate devices
                for k in range(i + 1, j):
                    mid = chain_present[k]
                    bx, by = coords[mid]
                    # Shift right by 100px, unless right side is occupied
                    right_occupied = any(
                        coords.get(d, (0, 0))[0] > bx
                        for d in device_names if d != mid and d in coords
                    )
                    if right_occupied:
                        coords[mid] = (bx - 100, by)  # shift left
                    else:
                        coords[mid] = (bx + 100, by)  # shift right

    return coords


def get_label_side(device_name, coords, all_links, all_device_names):
    """Determine which side to place a device's label box on.

    Rule (SKILL.md Section 4.3.1):
    - If ALL physical neighbors are to the LEFT  (nx < device_x) → place RIGHT
    - If ALL physical neighbors are to the RIGHT (nx > device_x) → place LEFT
    - Mixed or same-column only → default LEFT

    Returns 'left' or 'right'.
    """
    dx, _ = coords.get(device_name, (400, 400))
    neighbors_left = 0
    neighbors_right = 0

    for link in all_links:
        src = link['source'].split(':')[0]
        dst = link['target'].split(':')[0]
        neighbor = None
        if src == device_name and dst in all_device_names:
            neighbor = dst
        elif dst == device_name and src in all_device_names:
            neighbor = src
        if neighbor:
            nx, _ = coords.get(neighbor, (400, 400))
            if nx < dx:
                neighbors_left += 1
            elif nx > dx:
                neighbors_right += 1

    if neighbors_left > 0 and neighbors_right == 0:
        return 'right'
    return 'left'


def get_last_octet(subnet, position):
    """Extract the host address last octet from a subnet.
    position: 1 for source (.1), 2 for target (.2)
    """
    base = subnet.split('/')[0]
    parts = base.split('.')
    host = int(parts[3]) + position
    return f".{host}"

def generate_xml(devices, links, lab_title, lab_info=None, coords=None,
                 tunnel_overlays=None):
    if coords is None:
        coords = BASE_COORDS
    if tunnel_overlays is None:
        tunnel_overlays = []
    timestamp = datetime.now().isoformat()
    xml_content = DRAWIO_HEADER.format(timestamp=timestamp)
    octet_id_counter = 100  # ID counter for octet labels

    # 1. Add Title (top center)
    xml_content += f"""        <mxCell id="title" value="{lab_title}" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=16;fontStyle=1" vertex="1" parent="1">
          <mxGeometry x="200" y="40" width="400" height="40" as="geometry" />
        </mxCell>
"""

    # 2. Add Devices with smart label placement (SKILL.md Section 4.3.1)
    device_names_set = [d['name'] for d in devices]
    for device in devices:
        name = device['name']
        role = device.get('role', 'Router')
        lo0 = device.get('loopback0', 'N/A')

        x, y = coords.get(name, (100, 100))

        # Icon
        xml_content += f"""        <mxCell id="{name}" value="" style="{STYLE_ROUTER}" vertex="1" parent="1">
          <mxGeometry x="{x}" y="{y}" width="78" height="53" as="geometry" />
        </mxCell>
"""

        # Label — placed on the empty side (no connection lines)
        label_text = f"{name}&#10;{role}&#10;{lo0}"
        side = get_label_side(name, coords, links, device_names_set)
        label_x = x + 83 if side == 'right' else x - 105
        label_y = y - 7
        xml_content += f"""        <mxCell id="{name}_lbl" value="{label_text}" style="{STYLE_DEVICE_LABEL}" vertex="1" parent="1">
          <mxGeometry x="{label_x}" y="{label_y}" width="100" height="60" as="geometry" />
        </mxCell>
"""

    # 3. Add Links (white lines) with edge labels and IP octet annotations
    for link in links:
        src = link['source'].split(':')[0]
        dst = link['target'].split(':')[0]

        # Only draw link if both devices exist in this topology
        device_names = [d['name'] for d in devices]
        if src in device_names and dst in device_names:
            link_id = f"link_{src}_{dst}"
            src_int = link['source'].split(':')[1]
            dst_int = link['target'].split(':')[1]
            subnet = link.get('subnet', 'N/A')

            style = STYLE_LINK_DASHED if "Tunnel" in src_int or "Tunnel" in dst_int else STYLE_LINK_SOLID

            # Connection line
            xml_content += f"""        <mxCell id="{link_id}" value="" style="{style}" edge="1" parent="1" source="{src}" target="{dst}">
              <mxGeometry relative="1" as="geometry" />
            </mxCell>
            <mxCell id="{link_id}_lbl" value="{src_int} - {dst_int}&#10;{subnet}" style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];fontSize=10;" vertex="1" connectable="0" parent="{link_id}">
              <mxGeometry x="0" y="0" relative="1" as="geometry">
                <mxPoint as="offset" />
              </mxGeometry>
            </mxCell>
"""
            # IP last octet labels near each router interface
            src_x, src_y = coords.get(src, (100, 100))
            dst_x, dst_y = coords.get(dst, (100, 100))
            src_octet = get_last_octet(subnet, 1)
            dst_octet = get_last_octet(subnet, 2)

            # Position octets near the router side of the link
            # Offset to the right of the icon (+50px from icon x)
            octet_x = src_x + 50
            # Y near the interface exit (toward the target)
            src_octet_y = src_y + 60 if dst_y > src_y else src_y - 10
            dst_octet_y = dst_y - 10 if dst_y > src_y else dst_y + 60
            dst_octet_x = dst_x + 50

            xml_content += f"""        <mxCell id="octet_{octet_id_counter}" value="{src_octet}" style="{STYLE_OCTET_LABEL}" vertex="1" connectable="0" parent="1">
              <mxGeometry x="{octet_x}" y="{src_octet_y}" as="geometry" />
            </mxCell>
"""
            octet_id_counter += 1
            xml_content += f"""        <mxCell id="octet_{octet_id_counter}" value="{dst_octet}" style="{STYLE_OCTET_LABEL}" vertex="1" connectable="0" parent="1">
              <mxGeometry x="{dst_octet_x}" y="{dst_octet_y}" as="geometry" />
            </mxCell>
"""
            octet_id_counter += 1

    # 4. Add Tunnel Overlays (curved colored dotted arcs above physical topology)
    device_names = [d['name'] for d in devices]
    active_tunnel_types = set()
    for idx, tunnel in enumerate(tunnel_overlays):
        src_dev = tunnel['source'].split(':')[0]
        dst_dev = tunnel['target'].split(':')[0]
        if src_dev in device_names and dst_dev in device_names:
            xml_content += generate_tunnel_xml(tunnel, idx, coords)
            active_tunnel_types.add(tunnel.get('type', 'gre').lower())

    # 5. Add Legend Box (black fill, white text, bottom-right)
    legend_content = "Legend"
    if lab_info:
        legend_content += f"&#10;{lab_info}"
    legend_content += "&#10;&#x2014;&#x2014; Physical Link"
    # Add tunnel type entries if any tunnels are present
    for ttype in sorted(active_tunnel_types):
        label = TUNNEL_LEGEND_LABELS.get(ttype, ttype.upper())
        legend_content += f"&#10;....... {label}"

    # Determine legend Y based on lowest device
    max_y = max(coords.get(d['name'], (0, 0))[1] for d in devices)
    legend_y = max_y + 140
    legend_h = 80 + 15 * len(active_tunnel_types)

    xml_content += f"""        <mxCell id="legend" value="{legend_content}" style="{STYLE_LEGEND}" vertex="1" parent="1">
          <mxGeometry x="600" y="{legend_y}" width="180" height="{legend_h}" as="geometry" />
        </mxCell>
"""

    xml_content += DRAWIO_FOOTER
    return xml_content

def main():
    parser = argparse.ArgumentParser(description="Generate Draw.io XML from baseline.yaml")
    parser.add_argument("--baseline", required=True, help="Path to baseline.yaml")
    parser.add_argument("--lab", required=True, type=int, help="Lab number to generate for")
    parser.add_argument("--output", required=True, help="Output path for topology.drawio")

    args = parser.parse_args()

    # Use internal parser
    data = parse_simple_yaml(args.baseline)

    # 1. Determine Active Devices
    active_devices = []

    # Get Lab Definition
    lab_def = next((l for l in data['labs'] if int(l['number']) == args.lab), None)

    if not lab_def:
        print(f"Error: Lab {args.lab} not found in baseline.")
        sys.exit(1)

    required_device_names = lab_def.get('devices', [])

    # Filter Devices
    all_devices = data['core_topology']['devices'] + data.get('optional_devices', [])
    for d in all_devices:
        if d['name'] in required_device_names:
            active_devices.append(d)

    # 2. Determine Active Links
    active_links = []
    all_links = data['core_topology']['links'] + data.get('optional_links', [])

    for link in all_links:
        src = link['source'].split(':')[0]
        dst = link['target'].split(':')[0]
        if src in required_device_names and dst in required_device_names:
            active_links.append(link)

    # 3. Build lab info string for legend
    chapter = data.get('chapter', '')
    lab_info = f"{chapter} Lab {args.lab}"

    # 4. Compute layout coordinates (handles bypass link offset)
    layout_coords = compute_coords(required_device_names, active_links)

    # 5. Filter tunnel overlays for this lab
    active_tunnels = [
        t for t in data.get('tunnel_overlays', [])
        if str(t.get('lab', '')) == str(args.lab)
    ]

    # 6. Generate XML
    xml_output = generate_xml(
        active_devices,
        active_links,
        f"Lab {args.lab}: {lab_def['title']}",
        lab_info=lab_info,
        coords=layout_coords,
        tunnel_overlays=active_tunnels,
    )

    # 7. Write File
    with open(args.output, 'w') as f:
        f.write(xml_output)

    print(f"Successfully generated topology for Lab {args.lab} with {len(active_devices)} routers.")

if __name__ == "__main__":
    main()
