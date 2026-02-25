# BGP Lab 06 — Challenge Exercises: Communities & Policy Control

These challenges extend the core lab tasks. Complete the main workbook first before attempting these.

---

## Challenge 1 — Propagate Communities Across AS Boundaries

**Background:**

By default, Cisco IOS strips well-known and standard communities when routes are forwarded across eBGP session boundaries. However, you can allow community propagation from one AS into another with the right configuration.

**Challenge:**

R2 (ISP-A) currently strips any communities on routes it re-advertises to R3. Configure R2 so that it propagates the `65001:100` community it receives from R1 when forwarding routes to R3.

**Tasks:**
1. Verify the current state: does R3 see the `65001:100` community on 192.168.1.0/24 via R2?
2. Add the appropriate neighbor command on R2 to pass communities through to R3
3. Confirm R3 now sees `65001:100` on enterprise routes received via R2

**Expected Outcome:**
```
R3# show ip bgp 192.168.1.0
  Community: 65001:100   (arriving via R2's path)
```

**Hint:** The `send-community` command must be in place on both the receiving AND re-advertising side. R2 already has `send-community` to R3. What else might be needed?

---

## Challenge 2 — Implement `no-advertise` on a Specific Prefix

**Background:**

The `no-advertise` well-known community prevents a route from being advertised to ANY BGP neighbor — unlike `no-export` which only prevents advertisement beyond the local AS.

**Challenge:**

On R1, configure the 172.16.1.1/32 loopback prefix with the `no-advertise` community so that it remains in the local BGP table but is never sent to any BGP peer.

**Tasks:**
1. Create a prefix-list matching 172.16.1.1/32
2. Create a route-map that sets community `no-advertise` on that prefix
3. Apply the route-map using the appropriate BGP `network` route-map reference or as an outbound filter to all peers
4. Verify that R2, R3, and R4 do NOT receive 172.16.1.1/32

**Expected Outcome:**
```
R2# show ip bgp 172.16.1.1
(no entry)

R1# show ip bgp 172.16.1.1
  Community: no-advertise
```

**Reflection Question:** What is the practical use case for `no-advertise` vs `no-export`?

---

## Challenge 3 — Build a Community-Based Traffic Engineering Policy

**Background:**

Large ISPs use communities to allow customers to remotely trigger routing policy changes — for example, a customer can tag a prefix with a specific community to request the ISP to prepend the customer's AS-path, making that ISP path less preferred by the internet.

**Challenge:**

Implement a "remote trigger" policy on R1: any prefix received from R3 (ISP-B) that carries community `65003:200` should have R1 prepend AS 65001 twice before advertising to R2, making ISP-B less competitive as a transit path for those specific prefixes.

**Tasks:**
1. Create a community-list matching `65003:200`
2. Modify PREPEND-TO-ISP-B (or create a new route-map) to match `65003:200` and prepend `65001 65001`
3. On R3, manually set community `65003:200` on one of its loopback prefixes (e.g., 203.0.114.0/24) and advertise it to R1
4. Verify R2 sees 203.0.114.0/24 with a longer AS-path than the other ISP-B routes

**Expected Outcome:**
```
R2# show ip bgp 203.0.114.0
  AS-PATH: 65002 65001 65001 65001 65003   (prepended via policy)

R2# show ip bgp 203.0.113.0
  AS-PATH: 65002 65001 65003               (normal, no prepend)
```

---

## Challenge 4 — Extended Communities: Route-Target Simulation

**Background:**

BGP extended communities (64-bit) are used extensively in MPLS VPN and other service provider scenarios. While full MPLS is beyond the scope of this lab, you can practice the mechanics of setting and matching extended communities.

**Challenge:**

Configure R1 to set an extended community of type `rt` (route-target) with a value of `65001:1000` on the 192.168.1.0/24 prefix when advertising to R2.

**Tasks:**
1. Add `ip extcommunity-list standard ENTERPRISE-RT permit rt 65001:1000` on R1
2. Modify SET-COMMUNITY-OUT to also set `extcommunity rt 65001:1000 additive` on the 192.168.1.0/24 prefix
3. Ensure R2 receives the extended community by also adding `send-community extended` to the neighbor statement
4. Verify with `show ip bgp 192.168.1.0` on R2

**Note:** Extended community propagation requires `send-community extended` (or `send-community both`) in addition to the standard `send-community`. This is a common exam pitfall.

---

## Challenge 5 — Community Blackhole Route

**Background:**

BGP blackholing is a DDoS mitigation technique. A router under attack can tag a victim's prefix with a specific "blackhole" community, signaling upstream ISPs to drop traffic destined for that prefix at their edge — protecting the target network's bandwidth.

**Challenge:**

Implement a basic blackhole signal mechanism:

**Tasks:**
1. Define community `65001:9999` as the blackhole community on R1
2. Create a route-map on R1 that detects the `65001:9999` community on inbound routes from R4 and sets local-preference to 50 (traffic will be de-preferred)
3. On R4, manually tag 10.4.2.0/24 with community `65001:9999` using a route-map on its outbound advertisement to R1
4. Verify that R1 assigns local-preference 50 to 10.4.2.0/24 while 10.4.1.0/24 remains at the default (100)

**Expected Outcome:**
```
R1# show ip bgp 10.4.2.0
  Local preference: 50
  Community: 65001:9999

R1# show ip bgp 10.4.1.0
  Local preference: 100
```

**Reflection:** In a real-world scenario, the ISP would honor the blackhole community by routing the victim prefix to a Null0 interface. How would you implement that on R2?

---

## Challenge 6 — Community-Based Route Filtering (Conditional Advertisement)

**Background:**

Instead of using prefix-lists or AS-path ACLs to filter routes, you can use community-based filtering — which is more scalable because you can change policy on a remote router by changing a community tag rather than updating prefix-lists everywhere.

**Challenge:**

R1 should only advertise routes to R2 that carry community `65001:100`. All other routes (including the loopback 172.16.1.1/32 and the iBGP routes from R4) should be suppressed from the R2 advertisement.

**Tasks:**
1. Create a community-list matching `65001:100`
2. Create a route-map that: permits routes matching that community-list, denies everything else
3. Apply this route-map outbound to R2
4. Verify R2 only receives the three 192.168.x.0/24 prefixes

**Expected Outcome:**
```
R2# show ip bgp summary
10.1.12.1   ...  3   (only 3 prefixes from R1)

R2# show ip bgp | include 172.16.1.1
(no entry — loopback filtered)
```

**Caution:** Before applying, confirm R4's prefixes have `no-export` set — otherwise they will also be community-filtered. Think through the order of operations carefully.

---

## Challenge 7 — Automate Community Verification with a Python Script

**Background:**

In production networks, community verification is done programmatically. Write a Python script using Netmiko to automate the verification of community tags across all routers.

**Challenge:**

Create a script at `scripts/verify_communities.py` that:

1. Connects to R1, R2, R3, R4, R5 via telnet (ports 5001-5005)
2. On each router, runs `show ip bgp` and captures the output
3. Verifies the following conditions and prints PASS/FAIL for each:
   - R2 sees `65001:100` on 192.168.1.0/24
   - R1 sees `no-export` on 10.4.1.0/24
   - R3 sees `65003:500` on 10.5.1.0/24
   - R1 sees local-preference 120 on 10.5.1.0/24
   - R1 sees local-preference 200 on 198.51.100.0/24

**Starter Template:**
```python
from netmiko import ConnectHandler

routers = [
    {"name": "R1", "port": 5001},
    {"name": "R2", "port": 5002},
    {"name": "R3", "port": 5003},
    {"name": "R4", "port": 5004},
    {"name": "R5", "port": 5005},
]

def connect(port):
    return ConnectHandler(
        device_type="cisco_ios_telnet",
        host="127.0.0.1",
        port=port,
        username="",
        password="",
        secret="",
    )

def check(conn, prefix, expected_string, description):
    output = conn.send_command(f"show ip bgp {prefix}")
    result = "PASS" if expected_string in output else "FAIL"
    print(f"  [{result}] {description}")
    return result == "PASS"

# Your implementation here
```
