# Troubleshooting Challenges: EIGRP Lab 05

These challenges are designed to test your diagnostic skills.

**Instructions:**
1. Inject a fault using the corresponding script (e.g., `python3 scripts/fault_inject_1.py`).
2. Identify and resolve the issue on the routers.
3. Once resolved, or to start over, run the refresh script: `python3 scripts/refresh_lab.py`.

## Challenge 1: The "Secret" Mismatch (MD5)
**Script:** `scripts/fault_inject_1.py`
**Symptom:** R1 and R2 are physically connected, but the EIGRP adjacency has dropped. `show ip eigrp neighbors` is empty on both sides. Console logs on R1 show "authentication bad key".

**Goal:** Identify why MD5 authentication is failing and restore the secure adjacency.

---

## Challenge 2: Tagging Gone Missing
**Script:** `scripts/fault_inject_2.py`
**Symptom:** R5 is receiving the Hub loopback route (1.1.1.1/32) from R1, but the route is **not** tagged with `111`. The `show ip eigrp topology 1.1.1.1/32` output on R5 shows no `Internal tag` line.

**Goal:** Find where the tagging process is failing on R1 and restore the tag `111` on the Hub loopback route.

---

## Challenge 3: The Misguided Penalty
**Script:** `scripts/fault_inject_3.py`
**Symptom:** R1's offset list appears to be active, but the metric penalty is being applied to the wrong routes. Routes from R5 (5.5.5.5/32) that should be penalized are unaffected, while other routes are unexpectedly inflated.

**Goal:** Investigate the offset list ACL on R1. Determine if the access-list is matching the correct networks, and fix the mismatch.

---

## Solutions (Spoiler Alert!)

### Challenge 1: The "Secret" Mismatch (MD5) — Solution

**Symptom:** R1 and R2 are physically connected, but the EIGRP adjacency has dropped. `show ip eigrp neighbors` is empty on both sides. Console logs on R1 show "authentication bad key".

**Root Cause:** The MD5 key-chain password was changed from `SkynetSecret` to `WRONG_PASSWORD` on R2, causing authentication failure.

**Solution:**

On **R2**, correct the key-chain password to match R1:

```bash
R2# configure terminal
R2(config)# key chain SKYNET_MD5
R2(config-keychain)# key 1
R2(config-keychain-key)# key-string SkynetSecret
R2(config-keychain-key)# exit
R2(config-keychain)# exit
R2(config)# end
R2# write memory
```

**Verification:**

```bash
R1# show ip eigrp neighbors detail
EIGRP-IPv4 Neighbors for AS 100
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq
                                                   (sec)         (ms)       Cnt Num
0   10.0.12.2               Fa1/0                    13 00:02:15   15   200  0  25
   Version 15.3/2.0, Retrans: 0, Retries: 0, Prefixes: 8
   Authentication MD5, key-chain "SKYNET_MD5"
```

The neighbor adjacency should re-establish and show MD5 authentication active.

---

### Challenge 2: Tagging Gone Missing — Solution

**Symptom:** R5 is receiving the Hub loopback route (1.1.1.1/32) but it is not tagged with `111`.

**Root Cause:** The `distribute-list route-map TAG_HQ out FastEthernet1/0` was removed from R1's EIGRP router configuration, preventing the route-map from tagging routes sent to downstream routers.

**Solution:**

On **R1**, re-apply the distribute-list route-map configuration:

```bash
R1# configure terminal
R1(config)# router eigrp 100
R1(config-router)# distribute-list route-map TAG_HQ out FastEthernet1/0
R1(config-router)# end
R1# write memory
```

**Verification:**

Verify on **R1** that the distribute-list and route-map are in place:

```bash
R1# show run | section router eigrp
router eigrp 100
 ...
 distribute-list route-map TAG_HQ out FastEthernet1/0

R1# show route-map TAG_HQ
route-map TAG_HQ, permit, sequence 10
  Match clauses:
    ip address 11
  Set clauses:
    tag 111
  Policy routing matches: 0 packets, 0 bytes
route-map TAG_HQ, permit, sequence 20
  Match clauses:
  Set clauses:
  Policy routing matches: 0 packets, 0 bytes
```

Verify on **R5** that the tag is now visible:

```bash
R5# show ip eigrp topology 1.1.1.1/32
IP-EIGRP (AS 100): Topology entry for 1.1.1.1/32
  ...
        Internal tag is 111
```

---

### Challenge 3: The Misguided Penalty — Solution

**Symptom:** R1's offset list is applying the metric penalty to the wrong routes. R5 routes (5.5.5.5/32) are unaffected, while other routes are unexpectedly inflated.

**Root Cause:** The offset list ACL 55 on R1 was modified to match `3.3.3.3` (R3's loopback) instead of the correct R5 networks (`5.5.5.5` and `10.5.0.0 0.0.255.255`). This causes the offset to penalize R3's routes instead of R5's.

**Solution:**

On **R1**, correct the access-list to match R5's networks:

```bash
R1# configure terminal
R1(config)# no access-list 55
R1(config)# access-list 55 permit 5.5.5.5
R1(config)# access-list 55 permit 10.5.0.0 0.0.255.255
R1(config)# end
R1# write memory
```

**Verification:**

Verify the corrected ACL:

```bash
R1# show access-lists 55
Standard IP access list 55
    10 permit 5.5.5.5
    20 permit 10.5.0.0, wildcard bits 0.0.255.255
```

Verify that the offset list is now applied to R5's routes:

```bash
R1# show ip eigrp topology 5.5.5.5/32
EIGRP-IPv4 Topology Entry for AS(100)/ID(1.1.1.1) for 5.5.5.5/32
  State is Passive, Query origin flag is 1, 1 Successor(s), FD is 2339616
  Descriptor Blocks:
  10.0.12.2 (FastEthernet1/0), from 10.0.12.2, Send flag is 0x0
      Composite metric is (2339616/435200), route is Internal
      ...
```

The FD should be `2339616` (base `1839616` + offset `500000`). R3's routes (3.3.3.3/32) should return to their normal metric without the penalty.
