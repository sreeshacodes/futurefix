# Findings — Gear Line 3, 2–15 March 2026

| Machine | OEE | Availability | Performance | Quality |
|---|---|---|---|---|
| HOB-01 | 74% | 83% | 93% | 96% |
| HOB-02 | 71% | 86% | 87% | 95% |
| SHV-01 | 76% | 83% | 94% | 97% |

**HOB-02 is the worst performer (71% OEE)**, losing time through **Performance (87%)** —
not Availability or Quality, both of which are the best or tied-best of the three machines.
It isn't stopping more than the others; it's running slower than its ideal cycle time.

**Monday action:** Pull HOB-02's cycle times against `part_master`'s ideal times. If one part
number is consistently slow, it's a tooling/setup issue on that job. If every part is slow,
the machine needs a mechanical check (spindle speed, feed rate, tooling wear).