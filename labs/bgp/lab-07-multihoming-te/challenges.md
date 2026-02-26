# BGP Lab 07 — Challenge Exercises

These standalone challenges extend the core lab tasks. Each can be worked independently after completing the main workbook.

---

## Challenge 1: Equal-Cost Multipath for 192.168.3.0/24

The operations team wants to load-balance inbound traffic for 192.168.3.0/24 across both ISPs equally. The current MED configuration in Task 4 gives ISP-A preference.

**Objective:** Remove the MED differentiation for 192.168.3.0/24 and advertise it with an equal AS-path length and no MED to both ISPs. Then verify that both R2 and R3 see the same AS-path length and no MED value for this prefix.

**Acceptance criteria:**
- `show ip bgp 192.168.3.0` on R2 and R3 both show `metric 0` (or no metric) and AS-path `65001`
- R1's BGP table shows `192.168.3.0/24` advertised symmetrically to both peers

**Hints:**
- Remove or restructure the MED-setting statements in OUTBOUND-ISP-A and OUTBOUND-ISP-B
- Use `clear ip bgp * soft out` to re-advertise after policy changes

---

## Challenge 2: Floating Static Default Route as Failback

If both ISP BGP sessions fail simultaneously, R4 loses its conditional BGP default route and has no internet connectivity.

**Objective:** Add a static default route on R4 pointing to R1 (10.1.14.1) with an administrative distance of 210 (higher than BGP iBGP AD of 200). This floating static route should only be installed when the BGP default is absent.

**Acceptance criteria:**
- `show ip route 0.0.0.0` on R4 shows the BGP default (AD=200) while BGP is operational
- After simulating BGP failure (shut both ISP links on R1), `show ip route 0.0.0.0` on R4 shows the static default (AD=210)
- When ISP links are restored, the BGP default takes precedence again

**Hints:**
- Use `ip route 0.0.0.0 0.0.0.0 10.1.14.1 210` on R4
- Administrative distance is the tiebreaker between routing protocols for the same prefix

---

## Challenge 3: BGP Prefix Filtering at AS Boundary

ISP-A has requested that AcmeCorp not advertise the loopback summary prefix (172.16.1.1/32) to the internet. Only the three enterprise customer prefixes (192.168.1–3.0/24) should be advertised.

**Objective:** Add an outbound prefix-list on R1 to both ISP peers that:
- Permits 192.168.1.0/24, 192.168.2.0/24, 192.168.3.0/24
- Denies all other prefixes including 172.16.x.x loopbacks

**Acceptance criteria:**
- `show ip bgp neighbors 10.1.12.2 advertised-routes` on R1 shows ONLY the three 192.168.x.0/24 prefixes (no loopback /32s)
- `show ip bgp neighbors 10.1.13.2 advertised-routes` on R1 shows the same result
- Existing AS-path prepend policies still function correctly for 192.168.1.0/24 and 192.168.2.0/24

**Hints:**
- Build a prefix-list and apply it as an additional outbound filter using `neighbor <ip> prefix-list <name> out`
- When both a `route-map out` and a `prefix-list out` are configured, prefix-list filtering is applied first

---

## Challenge 4: IP SLA-Based Conditional Default with Reachability Probe

The conditional default in Task 5 relies on the presence of 198.51.100.0/24 in the BGP table. This works for BGP-level failures but does not detect black-hole scenarios where the BGP session stays up but packets are dropped.

**Objective:** Configure an IP SLA probe on R1 that sends ICMP echo to 198.51.100.1 (R2's Loopback1). Track the IP SLA with an object-tracking entry. Modify the conditional default route origination to use this track in combination with the BGP prefix check.

**Acceptance criteria:**
- `show ip sla statistics` on R1 shows the probe as success when R2's loopback is reachable
- `show track` on R1 shows the object as Up
- When the IP SLA target becomes unreachable (simulated by filtering ICMP on R2), the track goes Down and the conditional default is withdrawn from R4

**Hints:**
- `ip sla 1` / `icmp-echo 198.51.100.1` / `frequency 10`
- `ip sla schedule 1 life forever start-time now`
- `track 1 ip sla 1 reachability`
- The route-map condition can match track state using EEM or by attaching the track to a static route that acts as the sentinel
