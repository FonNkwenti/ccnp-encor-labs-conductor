# BGP Lab 01: Basic eBGP Peering — Challenge Exercises

These standalone challenges test your understanding of BGP fundamentals
without step-by-step guidance. Complete the core lab first.

---

## Challenge 1: Single-Peer Isolation

**Scenario:** Configure R1 to only peer with R2 (remove the R3 peering). Verify that R1 can still reach ISP-B prefixes (203.0.113.0/24) through the R2-R3 transit link.

**Success criteria:**
- R1 has only one BGP neighbor (R2)
- R1's BGP table shows ISP-B prefixes with AS-path `65002 65003`
- `ping 203.0.113.1 source 172.16.1.1` succeeds from R1

---

## Challenge 2: Peer Shutdown and Recovery

**Scenario:** Administratively shut down the R1-R2 eBGP session using `neighbor shutdown`. Observe the BGP table changes on R1, then restore the session.

**Success criteria:**
- After shutdown: R1 loses all R2-originated prefixes within the BGP hold timer
- R1's ISP-A routes shift to the R3 transit path (AS-path `65003 65002`)
- After `no neighbor shutdown`: session returns to Established and original best paths restore

---

## Challenge 3: BGP Timers Investigation

**Scenario:** Change the BGP keepalive and hold timers between R1 and R2 to 10/30 seconds (from the default 60/180). Verify the negotiated values.

**Success criteria:**
- `show ip bgp neighbors 10.1.12.2` on R1 shows hold time of 30 seconds
- Session remains Established after timer change
- Default timers remain on R1-R3 session (60/180)

---

## Challenge 4: BGP Network Statement Precision

**Scenario:** On R1, try advertising `192.168.0.0/16` (a supernet) into BGP without creating a matching route. Observe the result. Then create a static route to null0 for that prefix and re-check.

**Success criteria:**
- Without the static route: prefix does NOT appear in `show ip bgp`
- After `ip route 192.168.0.0 255.255.0.0 Null0`: the /16 appears in the BGP table
- Understand why BGP requires an exact match in the routing table
