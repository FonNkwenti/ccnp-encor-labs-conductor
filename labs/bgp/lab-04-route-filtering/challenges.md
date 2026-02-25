# BGP Lab 04 — Challenge Exercises: Route Filtering with Prefix-Lists

These challenges extend the core lab. Complete the main workbook before attempting these.

---

## Challenge 1: Prefix-Length Range Filtering

The security team wants R1 to also reject any prefix more specific than a /24 from ISP-A (to prevent route hijacking via more-specific advertisements).

**Task:** Modify the `FROM-ISP-A` prefix-list to:
1. Permit `198.51.100.0/24` exactly (as before)
2. Add a new entry to **deny any prefix from the `198.51.0.0/16` range that is longer than /24** using the `ge` modifier: `deny 198.51.0.0/16 ge 25`

Apply the change and verify using `show ip bgp neighbors 10.1.12.2 received-routes`.

**Expected result:** Any prefix in the `198.51.x.x/25` through `/32` range would be rejected. Only the exact `/24` is accepted.

---

## Challenge 2: Bidirectional Prefix Filtering on R4

Currently R4 only has an outbound filter. Add an **inbound** prefix-list on R4 to ensure it only accepts internal Enterprise prefixes from R1 (the `192.168.x.x/24` range) and ignores ISP prefixes that might be forwarded via iBGP.

**Task:**
1. Create a prefix-list `FROM-R1` on R4:
   - `permit 192.168.0.0/16 ge 24 le 24` — accept any /24 from the 192.168.0.0/16 range
   - `deny 0.0.0.0/0 le 32`
2. Apply `neighbor 172.16.1.1 prefix-list FROM-R1 in` on R4
3. Run `clear ip bgp 172.16.1.1 soft in`

**Expected result:** R4's BGP table contains only `192.168.1.0/24` (and similar enterprise prefixes). ISP prefixes like `198.51.100.0/24` are absent from R4's routing table.

---

## Challenge 3: Conditional Outbound Filtering with Named Prefix-Lists

Replace the current `TO-ISP-B` prefix-list with a more precise one that uses the `ge` and `le` length operators:

**Task:** Allow only prefixes from `192.168.0.0/16` that are exactly `/24` to be sent to ISP-B:
```
ip prefix-list TO-ISP-B-V2 permit 192.168.0.0/16 ge 24 le 24
ip prefix-list TO-ISP-B-V2 deny 0.0.0.0/0 le 32
```
Remove the old `TO-ISP-B` filter and apply `TO-ISP-B-V2`. Verify that all three enterprise /24 subnets would be permitted by this generalized rule (even though current policy only allows `.1`).

**Thought question:** What is the difference between `prefix-list permit 192.168.1.0/24` and `prefix-list permit 192.168.0.0/16 ge 24 le 24`? Which is more scalable as the enterprise grows?

---

## Challenge 4: Soft Reconfiguration vs. Route Refresh

Research and demonstrate the difference between soft reconfiguration and BGP Route Refresh (RFC 2918):

1. Remove `soft-reconfiguration inbound` from the R2 neighbor
2. Attempt `show ip bgp neighbors 10.1.12.2 received-routes` — observe the error
3. Issue `clear ip bgp 10.1.12.2 soft in` — IOS automatically uses Route Refresh (if supported by the peer) even without `soft-reconfiguration inbound`
4. Check whether IOS retains the received-routes view afterward

**Key question:** When is `soft-reconfiguration inbound` still necessary even with Route Refresh support? (Answer: when you need `received-routes` view independently of a reset trigger)

---

## Challenge 5: Audit and Document the Filtering Policy

Write a brief policy document (in a `policy.txt` file in this lab directory) that captures:

1. The business justification for each filter (why is this prefix blocked/permitted?)
2. The match count for each prefix-list entry after running the lab (from `show ip prefix-list`)
3. A description of what would break if each filter were removed

This exercise mimics a real-world change control process where network engineers must document the intent and impact of routing policy changes.
