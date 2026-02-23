# Incident Report Template

Use this template for Phase IV: Resolution & Reporting. Fill in each section as you work through the diagnosis.

---

## 1. Incident Summary

```
Incident ID: [INC-YYYY-NNNN]
Date/Time: [YYYY-MM-DD HH:MM]
Reported by: [student / lab context]
Severity: [High | Medium | Low]
Lab: [labs/<chapter>/lab-NN-<slug>/]

Problem Statement:
[One or two sentences describing the exact observable failure.
Example: "R3 is not forming an OSPF adjacency with R1 on Fa0/0.
No routes from R3 appear in R1's routing table."]
```

## 2. Methodology Applied

```
Selected Approach: [Top-Down | Bottom-Up | Divide and Conquer | Follow Traffic Path | Compare Configurations]

Rationale:
- [Why this methodology was chosen]
- [What symptom or evidence pointed to this choice]
```

## 3. Diagnostic Log

Chronological record — add one entry per investigation step:

```
[HH:MM] <Action taken>
        Command: <show command or tool used>
        Result: <what was observed>
        Conclusion: <what this means>

[HH:MM] <Next action>
        ...
```

Example:
```
[09:20] Ping test from R1 to R3 loopback — FAILED
        Command: ping 3.3.3.3 source 1.1.1.1
        Result: 5/5 packets lost
        Conclusion: No IP reachability; routing or adjacency issue

[09:22] Check OSPF neighbor table on R1
        Command: show ip ospf neighbor
        Result: R3 not listed
        Conclusion: Adjacency not forming; check OSPF config

[09:25] Check OSPF interface config on both ends
        Command: show ip ospf interface Fa0/0 (R1 and R3)
        Result: R1 Hello=10s Dead=40s; R3 Hello=20s Dead=80s
        ROOT CAUSE: Hello/Dead timer mismatch
```

## 4. Root Cause Analysis

```
Root Cause:
[Technical description of the fault]

Technical Details:
- [Specific config difference or misconfiguration]
- [Why it prevents normal operation]

Impact:
- [What broke as a result]
- [Which lab objectives are affected]
```

## 5. Resolution Action

```
Fix Applied on [Device]:
[config terminal commands used]

Verification:
[show command confirming fix]
[expected output]
```

## 6. Post-Resolution Verification

```
Test 1: [description]
Command: [command]
Result: [PASS / FAIL]

Test 2: [description]
Command: [command]
Result: [PASS / FAIL]

All original symptoms resolved: [YES / NO]
```

## 7. Lessons Learned

```
Root cause category: [Timer mismatch | Auth failure | Missing network stmt | Wrong AS | Passive interface | etc.]

Exam tip: [One sentence connecting this fault to a CCNP 350-401 exam objective]

Preventive check: [What to verify to avoid this in future labs]
```

## 8. Metrics

```
Time to identify root cause: [X minutes]
Time to resolution: [X minutes]
Lab objectives unblocked: [list]
```
