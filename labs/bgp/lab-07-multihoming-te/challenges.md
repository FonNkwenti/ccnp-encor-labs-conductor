# BGP Lab 07 — Challenge Exercises: Multihoming & Traffic Engineering

These challenges extend the core lab tasks. Complete the main workbook before attempting these. Each challenge is self-contained and can be done in any order after all four workbook tasks are verified.

---

## Challenge 1 — Per-Prefix Outbound TE with Three ISPs

**Difficulty:** Advanced

**Background:**

The lab topology has two ISPs, but real enterprise networks often multihome to three or more providers. Managing per-prefix outbound policy for three ISPs requires careful LP tiering so that each prefix has a clear primary, secondary, and tertiary exit path.

**Challenge:**

Extend the Lab 07 policy to support a hypothetical third ISP-C (AS 65010, peer address 10.1.17.2) by designing and implementing a three-ISP LP tiering scheme for the same three enterprise prefix groups.

**Tasks:**

1. Define the LP tiering logic: for each of the three prefixes (192.168.1.0/24, 192.168.2.0/24, 192.168.3.0/24), assign primary (LP=200), secondary (LP=150), and tertiary (LP=100) exits across the three ISPs. Document your tiering matrix before writing any configuration.

2. Create a third prefix-list `ISP-C-PREFIXES` matching the ISP-C prefix space. Create a new inbound route-map `LP-FROM-ISP-C` that assigns LP=200 to ISP-C prefixes, LP=120 to customer routes, and LP=150 to all others. Apply it inbound to the hypothetical ISP-C neighbor.

3. Extend the outbound TE route-maps (`TE-TO-ISP-A`, `TE-TO-ISP-B`) and create a new `TE-TO-ISP-C` to implement the 3-ISP prepending matrix: each prefix is prepended once toward the secondary ISP and three times toward the tertiary ISP.

**Success Criteria:**

- The LP tiering matrix is documented before any configuration is written
- Each enterprise prefix has a distinct primary, secondary, and tertiary exit based on LP
- The `TE-TO-ISP-C` route-map correctly implements the prepend lengths defined in the matrix
- `show ip bgp` on R1 shows consistent LP values matching the documented policy

---

## Challenge 2 — Replace MED with Community-Based Inbound TE

**Difficulty:** Advanced

**Background:**

MED has a critical limitation: it is only compared between routes from the same neighboring AS by default, making it ineffective as a multi-hop inbound TE signal. Large ISPs often provide a community-based TE signaling service where customers can tag their prefixes with specific communities to trigger AS-path prepending or LP adjustments on the ISP's routers — without needing MED at all.

**Challenge:**

Implement a community-based inbound TE system that replaces the `set metric` MED signals in Task 2 with a community-tagging scheme that R2 and R3 could act on.

**Tasks:**

1. Remove all `set metric` commands from `TE-TO-ISP-A` and `TE-TO-ISP-B`. Replace them with `set community` tags that signal intent:
   - Prefix preferred via ISP-A: add community `65001:200`
   - Prefix preferred via ISP-B: add community `65001:300`
   - Prefix load-balanced: add community `65001:400`

2. On R2, create an inbound route-map from R1 that reads the community tags and acts on them:
   - `65001:300` → set as-path prepend 65002 (R2 prepends itself once, making ISP-A longer)
   - `65001:200` → no change (ISP-A is preferred, do nothing)
   - Default → pass through

3. On R3, mirror the logic: community `65001:200` triggers a prepend of 65003, community `65001:300` passes through.

**Success Criteria:**

- No `set metric` commands remain in `TE-TO-ISP-A` or `TE-TO-ISP-B`
- R2's BGP table shows a self-prepended AS-path for prefixes tagged `65001:300`
- The same prefix arrives at R3 with a shorter AS-path (no prepend) confirming asymmetric treatment
- `show ip bgp <prefix>` on R2 and R3 shows the expected AS-path difference

---

## Challenge 3 — Floating Static Default as Conditional Default Failover

**Difficulty:** Intermediate

**Background:**

The conditional default route in Task 4 withdraws the default from R4 when ISP-A is down. This protects R4 from a black hole — but if ISP-B is still reachable, R4 should ideally still have internet access via ISP-B. A floating static default with a high administrative distance provides a fallback that activates only when the BGP-learned default is absent.

**Challenge:**

Implement a two-tier default route architecture on R4 so that:
- When ISP-A is up: R4 uses the BGP-learned default (AD=20) from R1
- When ISP-A is down but ISP-B is up: R4 uses a floating static default (AD=254) pointing toward R1

**Tasks:**

1. On R4, add a floating static default route with administrative distance 254 pointing toward R1's Fa0/0 address (10.1.14.1):

   ```
   ip route 0.0.0.0 0.0.0.0 10.1.14.1 254
   ```

2. On R1, add a second conditional default origination check: originate a default to R4 when ISP-B (203.0.113.0/24) is reachable, even if ISP-A is down. This requires a second route-map condition or an expanded COND-DEFAULT prefix-list.

3. Verify the failover behavior: shut R2's Fa0/0 (ISP-A down). Confirm R4 still has a default route, now via R1-R3 (ISP-B path). Then also shut R3's Fa1/0 (both ISPs down). Confirm R4's default falls back to the floating static.

**Success Criteria:**

- When both ISPs are up, R4's default is BGP-learned (AD=20)
- When ISP-A is down and ISP-B is up, R4 still has a BGP-learned default sourced from the ISP-B condition check
- When both ISPs are down, R4's default is the floating static (AD=254), confirmed by `show ip route 0.0.0.0` showing `[254/0]`

---

## Challenge 4 — Local Preference from ISP Community Tags

**Difficulty:** Advanced

**Background:**

Major ISPs use communities to communicate route category information to their customers. For example, an ISP might tag routes with `65002:100` for its own network routes, `65002:200` for peer routes, and `65002:300` for customer routes. An enterprise receiving these community-tagged routes can automatically apply LP policy without maintaining prefix-lists — making the policy self-adapting as the ISP's route table evolves.

**Challenge:**

Replace the prefix-list-based LP matching in `LP-FROM-ISP-A` and `LP-FROM-ISP-B` with community-based LP matching, simulating ISP community signaling.

**Tasks:**

1. On R2, create outbound route-maps to tag its own prefixes with community signals before sending them to R1:
   - R2's own prefixes (198.51.x.x): set community `65002:100`
   - Customer routes (community 65003:500 visible via R3): set community `65002:300`
   - All others: set community `65002:200`

   Apply this route-map outbound to R1 (neighbor 10.1.12.1).

2. Mirror the tagging on R3 using community values `65003:100`, `65003:300`, and `65003:200`.

3. Rebuild `LP-FROM-ISP-A` to match on community values instead of prefix-lists:
   - community 65002:100 → LP=200
   - community 65002:300 → LP=120
   - community 65002:200 → LP=150
   - Default catch-all → LP=150

4. Delete the `ISP-A-PREFIXES` and `ISP-B-PREFIXES` prefix-lists. Confirm the LP policy still works correctly without them.

**Success Criteria:**

- R1's `show ip bgp` shows the same LP values as in the Task 1 solution
- `show ip community-list` on R1 shows community-lists replacing the prefix-lists
- No `ISP-A-PREFIXES` or `ISP-B-PREFIXES` prefix-lists exist in the running config
- `show ip bgp 198.51.100.0` shows LP=200 with community `65002:100` visible on the path

---

## Challenge 5 — Graduated AS-Path Prepending for Load Shifting

**Difficulty:** Intermediate

**Background:**

In production networks, traffic shifts are rarely binary (all ISP-A or all ISP-B). Graduated prepending — prepending once, twice, or three times — creates a spectrum of preference that allows the network engineer to shift load gradually and observe the impact before committing to a full steering decision. This is particularly useful when dealing with congested ISP links or during capacity migration.

**Challenge:**

Implement a graduated prepending matrix for the three enterprise prefixes. Instead of using a fixed 3x prepend for the non-preferred ISP, implement three distinct prepend levels to create a measurable LP gradient visible in the BGP tables of both ISPs.

**Tasks:**

1. Redesign the TE route-maps to use graduated prepending:
   - 192.168.1.0/24: prepend 1x to ISP-B (`set as-path prepend 65001`)
   - 192.168.2.0/24: prepend 2x to ISP-A (`set as-path prepend 65001 65001`)
   - 192.168.3.0/24: prepend 3x to both ISPs (equal MED, gradual fade on both sides)

2. Apply the updated route-maps and soft-reset both outbound sessions.

3. Document the AS-path length and MED visible on R2 and R3 for each of the three prefixes in a verification table.

**Success Criteria:**

- `show ip bgp <prefix>` on R2 shows three distinct AS-path lengths for the three enterprise prefixes
- `show ip bgp <prefix>` on R3 shows three distinct AS-path lengths (different from R2's view)
- The verification table is completed and reflects the actual output from R2 and R3
- No 3x prepend remains for 192.168.1.0/24 toward ISP-B — it should be 1x only

---

## Challenge 6 — ISP-to-ISP MED-Based Path Preference (R2 to R3)

**Difficulty:** Advanced

**Background:**

The Lab 07 topology includes a direct link between R2 (ISP-A) and R3 (ISP-B) on the 10.1.23.0/30 subnet. This creates an interesting scenario: R2 and R3 each see the enterprise prefixes both directly from R1 and via each other. By configuring MED values on this ISP-to-ISP link, you can influence which AS is the preferred transit path when the two ISPs exchange enterprise prefixes.

**Challenge:**

Configure R2 and R3 to use MED values on their mutual eBGP session to establish a clear primary/secondary relationship for enterprise prefix transit.

**Tasks:**

1. On R2, create an outbound route-map to R3 that sets MED on enterprise prefixes:
   - 192.168.1.0/24 (ISP-A preferred): MED=10 (advertising that R2 is a good exit toward this prefix)
   - 192.168.2.0/24 (ISP-B preferred): MED=200 (advertising that R2 is a poor exit toward this prefix)
   - 192.168.3.0/24: MED=100

2. Mirror the logic on R3's outbound to R2:
   - 192.168.2.0/24: MED=10
   - 192.168.1.0/24: MED=200
   - 192.168.3.0/24: MED=100

3. Enable `bgp always-compare-med` on both R2 and R3 so that the MED values from R1 (AS 65001) and from each other are compared in path selection.

4. Verify that R3's BGP table prefers the direct path from R1 for 192.168.2.0/24 (MED=10 from R1 direct is still lower than MED=10 from R2 for the same prefix — check what the AS-path lengths and MED values look like with `always-compare-med` active).

**Success Criteria:**

- Both R2 and R3 have `bgp always-compare-med` configured
- `show ip bgp 192.168.1.0` on R3 shows that the path via R2 is no longer best (R1 direct path with AS-path prepend is longer, but R2's MED=10 signal makes R2 the preferred transit for this prefix when the always-compare-med override is active — or alternatively, explain the actual selection result)
- No routing loops are introduced (verify with traceroute from R5 toward enterprise prefixes)
- A written analysis of two sentences explains why `bgp always-compare-med` must be enabled consistently across an entire AS

---

## Challenge 7 — Automate LP Policy Changes Using Netmiko

**Difficulty:** Intermediate

**Background:**

Traffic engineering policy changes are routine operations in production networks — congestion events, ISP maintenance windows, and traffic profiling all require LP or prepend adjustments. Automating these changes reduces the risk of manual error and enables rapid response. This challenge builds a Python tool that applies LP policy changes and verifies the result programmatically.

**Challenge:**

Create a script at `scripts/te_policy.py` that applies LP policy updates to R1 and verifies the new LP values in the BGP table.

**Tasks:**

1. Write a function `apply_lp_policy(neighbor_ip, route_map_name)` that connects to R1 via Netmiko (telnet, port 5001) and applies the specified route-map to the specified neighbor inbound, then issues `clear ip bgp <neighbor_ip> soft in`.

2. Write a function `verify_lp(prefix, expected_lp, via_next_hop)` that connects to R1, runs `show ip bgp <prefix>`, parses the output for the LocPrf value on the path via `via_next_hop`, and returns True if the value matches `expected_lp`.

3. Write a `main()` function that:
   - Applies `LP-FROM-ISP-A` inbound to 10.1.12.2
   - Applies `LP-FROM-ISP-B` inbound to 10.1.13.2
   - Waits 5 seconds for convergence
   - Runs `verify_lp` for each of the following conditions and prints PASS/FAIL:
     - 198.51.100.0/24 via 10.1.12.2 should be LP=200
     - 203.0.113.0/24 via 10.1.13.2 should be LP=200
     - 10.5.1.0/24 via 10.1.13.2 should be LP=120

**Starter Template:**

```python
import time
from netmiko import ConnectHandler

R1 = {
    "device_type": "cisco_ios_telnet",
    "host": "127.0.0.1",
    "port": 5001,
    "username": "",
    "password": "",
    "secret": "",
}

def connect():
    return ConnectHandler(**R1)

def apply_lp_policy(conn, neighbor_ip, route_map_name):
    cmds = [
        "router bgp 65001",
        f"neighbor {neighbor_ip} route-map {route_map_name} in",
        "end",
        f"clear ip bgp {neighbor_ip} soft in",
    ]
    conn.send_config_set(cmds[:-1])
    conn.send_command(cmds[-1])

def verify_lp(conn, prefix, expected_lp, via_next_hop):
    output = conn.send_command(f"show ip bgp {prefix}")
    # Parse output for LocPrf on the path via via_next_hop
    # Return True if expected_lp matches, False otherwise
    pass

def main():
    conn = connect()
    apply_lp_policy(conn, "10.1.12.2", "LP-FROM-ISP-A")
    apply_lp_policy(conn, "10.1.13.2", "LP-FROM-ISP-B")
    time.sleep(5)

    checks = [
        ("198.51.100.0", 200, "10.1.12.2", "ISP-A prefix via ISP-A gets LP=200"),
        ("203.0.113.0",  200, "10.1.13.2", "ISP-B prefix via ISP-B gets LP=200"),
        ("10.5.1.0",     120, "10.1.13.2", "Customer route gets LP=120"),
    ]

    for prefix, expected, via, description in checks:
        result = verify_lp(conn, prefix, expected, via)
        status = "PASS" if result else "FAIL"
        print(f"  [{status}] {description}")

    conn.disconnect()

if __name__ == "__main__":
    main()
```

**Success Criteria:**

- The script connects to R1 and applies both route-maps without error
- The script prints PASS for all three LP verification checks
- `verify_lp` correctly parses the `show ip bgp` output and extracts the LocPrf value for the specific next-hop path
- The script handles the case where `soft-reconfiguration inbound` is not enabled (the `show ip bgp neighbors received-routes` fallback) and prints a warning if the inbound table is unavailable
