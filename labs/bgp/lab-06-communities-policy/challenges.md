# BGP Lab 06 — Challenge Exercises

These standalone challenges extend the core lab tasks. Each can be attempted
independently after completing the main lab. No step-by-step guidance is provided.

---

## Challenge 1: Additive Community Stacking

The network team wants enterprise prefixes sent to ISP-B to carry both a community
value identifying the source AS (`65001:200`) and a second value classifying the
traffic type (`65001:500` for production traffic). The AS-path prepend must remain.

Configure R1's outbound policy to ISP-B so that both community values are present
simultaneously on enterprise prefixes when received by R3 — without removing the
prepend. Verify that R3 sees `Community: 65001:200 65001:500` on 192.168.x.x routes.

**Hint:** The `set community` command overwrites by default. Research the keyword that
makes it additive instead.

---

## Challenge 2: Community-Based Conditional Advertisement to R5

DataStream (R5) should only receive ISP-B's public prefixes (203.0.113.0/24 and
203.0.114.0/24) — not the internal range already tagged with `no-export`. Extend the
outbound policy on R3 so that:

- 203.0.115.0/24 continues to be tagged with `no-export`
- 203.0.113.0/24 and 203.0.114.0/24 are tagged with community `65003:300` before
  being sent to R5
- R5 receives a route-map inbound that matches `65003:300` and sets local-preference
  120 for ISP-B public routes

Verify: `show ip bgp 203.0.113.0` on R5 shows `localpref 120` and `Community: 65003:300`.

---

## Challenge 3: Strip Communities at the eBGP Boundary

ISP-A (R2) has noticed that Acme's iBGP-tagged community values are leaking into the
ISP-A BGP table — specifically, routes tagged with `local-AS` are still visible to R2
with the community attribute intact. In production, communities should be stripped at
the eBGP exit to prevent internal policy metadata from leaking to upstream ISPs.

Configure R1's outbound policy to ISP-A so that any community tagged `local-AS` is
removed before the route is sent. All other routes should still carry their appropriate
community values.

**Constraint:** Do not use a `no neighbor ... send-community` statement — community
propagation must remain active for non-local-AS routes.

**Hint:** Research `set community none` in a route-map and how to conditionally strip
a specific community value using a community-list match.

---

## Challenge 4: Dynamic Community Matching with Regex-Style Community Lists

Acme's policy team wants to filter all inbound routes from ISP-A that carry any
community in the `65002:*` range (any NN value from 0–65535), setting local-preference
to 120 for those routes and 100 for all others.

Using an extended community-list with a regex match (or a range-based community list),
configure R1's inbound policy from R2 so that:

- Any prefix from AS 65002 carrying a community value starting with `65002:` receives
  local-preference 120
- All other ISP-A routes receive local-preference 200 (existing behavior)
- The `local-AS` tagging for 198.51.102.0/24 must still function

Verify with `show ip bgp` on R1 — routes from R2 carrying `65002:*` tags should show
`localpref 120`, others `localpref 200`.
