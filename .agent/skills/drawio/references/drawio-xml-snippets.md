# Draw.io XML Reference Snippets

Ready-to-paste XML for all standard diagram elements. Copy and adapt for each lab's `topology.drawio`.

## Title Cell

```xml
<mxCell id="title" value="Lab N: Title Here" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=16;fontStyle=1" vertex="1" parent="1">
  <mxGeometry x="200" y="40" width="400" height="40" as="geometry" />
</mxCell>
```

## Device Icons

**Router (c7200 or c3725):**
```xml
<mxCell id="R1" value="" style="shape=mxgraph.cisco.routers.router;fillColor=#036897;strokeColor=#ffffff;strokeWidth=2;verticalLabelPosition=bottom;verticalAlign=top;align=center;outlineConnect=0;" vertex="1" parent="1">
  <mxGeometry x="400" y="200" width="78" height="53" as="geometry" />
</mxCell>
```

**Layer 3 Switch:**
```xml
<mxCell id="SW1" value="" style="shape=mxgraph.cisco.switches.layer_3_switch;fillColor=#036897;strokeColor=#ffffff;strokeWidth=2;" vertex="1" parent="1">
  <mxGeometry x="400" y="350" width="78" height="53" as="geometry" />
</mxCell>
```

**Layer 2 Switch:**
```xml
<mxCell id="SW2" value="" style="shape=mxgraph.cisco.switches.workgroup_switch;fillColor=#036897;strokeColor=#ffffff;strokeWidth=2;" vertex="1" parent="1">
  <mxGeometry x="400" y="350" width="78" height="53" as="geometry" />
</mxCell>
```

## Device Labels

**Label positioned left of icon** (`label_x = device_x - 105`, `label_y = device_y - 7`):
```xml
<mxCell id="R1_lbl" value="R1&#10;Hub/ABR&#10;10.1.1.1/32" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=top;whiteSpace=wrap;rounded=0;fontSize=11;fontStyle=1" vertex="1" parent="1">
  <mxGeometry x="295" y="193" width="100" height="60" as="geometry" />
</mxCell>
```

**Label positioned right of icon** (`label_x = device_x + 83`, `label_y = device_y - 7`):
```xml
<mxCell id="R2_lbl" value="R2&#10;Spoke&#10;10.2.2.2/32" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=top;whiteSpace=wrap;rounded=0;fontSize=11;fontStyle=1" vertex="1" parent="1">
  <mxGeometry x="583" y="193" width="100" height="60" as="geometry" />
</mxCell>
```

## Connection Lines

**Standard physical link (white, width 2):**
```xml
<mxCell id="link_R1_R2" value="" style="endArrow=none;html=1;strokeWidth=2;strokeColor=#FFFFFF;fillColor=#f5f5f5;" edge="1" parent="1" source="R1" target="R2">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

**Link with interface/subnet edge label:**
```xml
<mxCell id="link_R1_R2_lbl" value="Fa1/0 - Fa0/0&#10;10.12.0.0/30" style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];fontSize=10;" vertex="1" connectable="0" parent="link_R1_R2">
  <mxGeometry relative="1" as="geometry"><mxPoint as="offset"/></mxGeometry>
</mxCell>
```

## IP Last Octet Labels

Place near the router's interface exit point on the connection line:
```xml
<mxCell id="R1_Fa1_0_octet" value=".1" style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];fontSize=10;" vertex="1" connectable="0" parent="1">
  <mxGeometry x="450" y="260" as="geometry" />
</mxCell>
<mxCell id="R2_Fa0_0_octet" value=".2" style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];fontSize=10;" vertex="1" connectable="0" parent="1">
  <mxGeometry x="520" y="260" as="geometry" />
</mxCell>
```

## Legend Box

```xml
<mxCell id="legend" value="Legend&#10;— Physical Link&#10;- - - Tunnel Link&#10;EIGRP AS 100" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#000000;strokeColor=#FFFFFF;fontColor=#FFFFFF;fontSize=10;align=left;verticalAlign=top;spacingLeft=8;spacingTop=8;" vertex="1" parent="1">
  <mxGeometry x="600" y="700" width="180" height="100" as="geometry" />
</mxCell>
```

---

## Tunnel Overlays

### GRE Tunnel Arc (white dotted, curved above devices)

**Algorithm**: `arc_y = min(source_y, target_y) - 100`; waypoints at `(source_x+39, arc_y)` and `(target_x+39, arc_y)`.

```xml
<mxCell id="tunnel_R1_R6" value="" style="endArrow=none;html=1;strokeWidth=1;strokeColor=#FFFFFF;fillColor=none;dashed=1;dashPattern=1 4;curved=1;exitX=0.5;exitY=0;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="R1" target="R6">
  <mxGeometry relative="1" as="geometry">
    <Array as="points">
      <mxPoint x="439" y="100"/>
      <mxPoint x="239" y="100"/>
    </Array>
  </mxGeometry>
</mxCell>
<mxCell id="tunnel_R1_R6_lbl" value="Tunnel8 - Tunnel8&#10;172.16.16.0/30&#10;[GRE]" style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];fontSize=10;" vertex="1" connectable="0" parent="tunnel_R1_R6">
  <mxGeometry relative="1" as="geometry"><mxPoint as="offset"/></mxGeometry>
</mxCell>
```

### Tunnel Endpoint Octet Labels (parent="1", near top of device)

Source gets `.1` at `(source_x+44, source_y-15)`; target gets `.2` at `(target_x+44, target_y-15)`:
```xml
<mxCell id="tunnel_R1_R6_src_octet" value=".1"
  style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];fontSize=10;"
  vertex="1" connectable="0" parent="1">
  <mxGeometry x="444" y="185" as="geometry" />
</mxCell>
<mxCell id="tunnel_R1_R6_dst_octet" value=".2"
  style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];fontSize=10;"
  vertex="1" connectable="0" parent="1">
  <mxGeometry x="244" y="185" as="geometry" />
</mxCell>
```

### Tunnel Color Reference

| Tunnel Type | Color     | Hex       |
|-------------|-----------|-----------|
| GRE         | White     | `#FFFFFF` |
| MPLS        | Orange    | `#FF6600` |
| IPsec VPN   | Red       | `#FF0000` |
| VXLAN       | Cyan      | `#00AAFF` |
| L2TP        | Purple    | `#AA00FF` |
| Other       | Yellow    | `#FFFF00` |

---

## Bypass-Link Layout (Offset to Avoid Link-Through-Device)

When a bypass link connects R1→R3 but R2 is at the same X coordinate between them, offset R2 right by ~100px:

```
Before (wrong):        After (correct):
R1 (400, 200)          R1 (400, 200)
|                     / \
R2 (400, 400)        R2 (500, 400)   ← shifted right
|                      \
R3 (400, 600)           R3 (400, 600)
```

Adjust R2's label and octet labels to follow the new coordinates.
