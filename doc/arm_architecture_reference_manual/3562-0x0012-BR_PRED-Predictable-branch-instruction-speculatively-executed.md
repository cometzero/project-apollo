# ​0x0012, BR_PRED, Predictable branch instruction speculatively executed

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0012--BR-PRED--Predictable-branch-instruction-speculatively-executed>

##### `0x0012`, BR\_PRED, Predictable branch instruction speculatively executed

The counter counts each branch or other change in the program flow that the branch prediction resources are capable of predicting.

If all branches are subject to prediction, for example a BTB or BTAC, then all branches are predictable branches.

If branches are decoded before the predictor, so that the branch prediction logic dynamically predicts only some branches, for example conditional and indirect branches, then it is IMPLEMENTATION DEFINED whether other branches are counted as predictable branches. Arm recommends that all branches are counted.

An implementation might include other structures that predict branches, such as a loop buffer that predicts short backwards direct branches as taken. Each execution of such a branch is a predictable branch. Terminating the loop might generate a misprediction event that is counted by [BR\_MIS\_PRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0010--BR-MIS-PRED--Branch-instruction-speculatively-executed--mispredicted-or-not-predicted?lang=en#event_br_mis_pred).

If no program-flow prediction resources are implemented, this event is optional, but Arm recommends that [BR\_PRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0012--BR-PRED--Predictable-branch-instruction-speculatively-executed?lang=en#event_br_pred) counts all branches.

It is IMPLEMENTATION DEFINED when the branch is counted. Arm recommends that it is counted when the branch is resolved, that is, at the same point in the instruction pipeline as when the [BR\_MIS\_PRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0010--BR-MIS-PRED--Branch-instruction-speculatively-executed--mispredicted-or-not-predicted?lang=en#event_br_mis_pred) event would be counted if the branch resolves as mispredicted.

PMCEID0\_EL0[18] reads as 1 if this event is implemented and 0 otherwise.
