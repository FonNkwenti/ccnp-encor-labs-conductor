# BGP Lab 09 — Standalone Challenges

These challenges extend the core lab tasks. Each is self-contained and does not require the previous challenge to be complete. Work from the Lab 09 solution state as your starting point.

---

## Challenge 1: Key Rotation Without Session Downtime

BGP MD5 keys must be rotated quarterly per security policy. A naive approach — removing the old password before applying the new one — drops the session and causes a routing outage. Your challenge: research and demonstrate a zero-downtime key rotation procedure on the R1-R2 eBGP session.

**Hint:** Cisco IOS supports `neighbor <ip> password` being changed live. The TCP session resets, but re-establishes immediately with the new key if both sides are changed within the BGP hold-time window (typically 90 seconds). Design a procedure using the BGP hold timer to your advantage.

**Success criteria:**
- Change R1's R2 neighbor password to `BGP_LAB_KEY_V2`
- Change R2's R1 neighbor password to `BGP_LAB_KEY_V2` within 90 seconds
- R1's BGP session to R2 recovers automatically without manual clearing
- `show ip bgp neighbors 10.1.12.2 | include password|state` confirms `MD5 password configured` and `Established`

---

## Challenge 2: Maximum-Prefix with Automatic Restart

The current maximum-prefix configuration requires manual intervention to recover a torn-down session. Reconfigure R1's maximum-prefix on the R2 and R3 neighbors to auto-restart after a 5-minute cooldown period.

**Success criteria:**
- `neighbor 10.1.12.2 maximum-prefix 200 80 restart 5` and same for R3 neighbor
- `show ip bgp neighbors 10.1.12.2 | include Maximum` confirms `restart 5`
- Trigger the limit (temporarily lower to `maximum-prefix 1`), observe auto-recovery without manual `clear ip bgp`
- Restore the correct limit of 200 before completing the challenge

---

## Challenge 3: Expand Bogon Filtering to Cover RFC 6890 Allocations

The current BOGON-PREFIXES list covers the most common ranges. Expand it on R1 to also include:

- `100.64.0.0/10` — Shared Address Space (RFC 6598, carrier-grade NAT)
- `192.0.0.0/24` — IETF Protocol Assignments (RFC 6890)
- `198.51.100.0/24` — Documentation (TEST-NET-2)
- `203.0.113.0/24` — Documentation (TEST-NET-3)

**Note:** The TEST-NET ranges (198.51.100.0/24 and 203.0.113.0/24) are used by R2 and R3 in this lab as simulated ISP prefixes. Adding them to the bogon filter will break reachability — document this real-world trade-off in your lab notes and then remove those two entries after testing.

**Success criteria:**
- Four new entries added to BOGON-PREFIXES (without removing existing nine)
- `show ip prefix-list BOGON-PREFIXES` shows 13 entries total
- After removing the TEST-NET entries: 11 entries, ISP prefixes still visible in R1's BGP table

---

## Challenge 4: iBGP Session Security Audit Report

Generate a security audit summary for the entire BGP topology after all Lab 09 tasks are complete. The report must be produced using only show commands — no configuration changes.

For each BGP session, capture and document:

| Session | MD5 Configured | TTL Security | Max-Prefix Limit | Session State |
|---------|---------------|--------------|-----------------|---------------|
| R1 ↔ R2 | ? | ? | ? | ? |
| R1 ↔ R3 | ? | ? | ? | ? |
| R2 ↔ R3 | ? | ? | ? | ? |
| R3 ↔ R5 | ? | ? | ? | ? |
| R1 ↔ R4 | ? | ? | ? | ? |
| R1 ↔ R6 | ? | ? | ? | ? |

Commands to use:
- `show ip bgp summary` — session state and prefix counts
- `show ip bgp neighbors <ip> | include password|TTL|Maximum|state` — security attributes

**Success criteria:**
- All six rows of the table populated from actual `show` command output
- Identify which sessions are missing TTL security (iBGP sessions) and explain why GTSM is not applied to loopback-sourced multi-hop sessions
- Identify any session where max-prefix is not configured and propose an appropriate limit
