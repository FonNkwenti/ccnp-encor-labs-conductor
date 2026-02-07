# CCNP ENCOR Lab Series

A comprehensive set of hands-on labs for the Cisco CCNP ENCOR (350-401) exam.

## Lab Chapters

| Chapter | Description |
|---------|-------------|
| [labs/eigrp](labs/eigrp) | EIGRP configuration, optimization & troubleshooting |
| [labs/ospf](labs/ospf) | OSPF multi-area design & verification |
| [labs/bgp](labs/bgp) | BGP path selection & filtering |
| [labs/ip-services](labs/ip-services) | DHCP, NAT, FHRP, NTP |
| [labs/security](labs/security) | AAA, ACLs, VPNs |
| [labs/automation](labs/automation) | Python, NETCONF, Ansible |
| [labs/integration](labs/integration) | Multi-protocol challenges |

## Getting Started

1. Set up GNS3 on Apple M1 (see `.agent/skills/gns3/SKILL.md` for constraints)
2. Load Cisco IOS images (c3725, c7200)
3. Navigate to a lab and follow the workbook

## Development

Lab creation uses Antigravity skills in `.agent/skills/`. See [docs/README.md](docs/README.md).
