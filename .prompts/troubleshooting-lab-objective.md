
  I'm working on EIGRP lab-06 (filtering-control), Objective 1. My configuration
  on R3 is not producing the expected results.

  Do NOT fix it for me. Instead, use the cisco-troubleshooting skill to analyze
  WHY my configuration is technically wrong.

  Reference:
  - The initial-configs in labs/eigrp/lab-06-filtering-control/initial-configs/
    to understand the baseline state
  - The workbook in labs/eigrp/lab-06-filtering-control/workbook.md for device
    access info and lab objectives
  - The expected solution in labs/eigrp/lab-06-filtering-control/solutions/
    ONLY if needed to understand the objective — do NOT show me the answer

  Here is the config I applied to R3:

  ip prefix-list TAG_R5 seq 10 permit 5.5.5.5/32
  ip prefix-list TAG_R5 seq 20 permit 10.5.0.0/16
  !
  route-map TAG-R5 permit 10
   match ip address prefix-list TAG_R5
   set tag 555
  !
  route-map TAG-R5 permit 20

  router eigrp 100
   passive-interface Loopback0
   network 3.3.3.3 0.0.0.0
   network 10.0.23.0 0.0.0.3
   network 10.0.35.0 0.0.0.3
   distribute-list route-map TAG_R5 out FastEthernet0/0
   no auto-summary
   eigrp router-id 3.3.3.3

  Explain technically why this isn't working. What concept am I misunderstanding?
