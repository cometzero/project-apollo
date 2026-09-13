# ​0x0010, BR_MIS_PRED, Branch instruction speculatively executed, mispredicted or not predicted

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0010--BR-MIS-PRED--Branch-instruction-speculatively-executed--mispredicted-or-not-predicted>

##### `0x0010`, BR\_MIS\_PRED, Branch instruction speculatively executed, mispredicted or not predicted

The counter counts each correction to the predicted program flow that occurs because of a misprediction from, or no prediction from, the branch prediction resources and that relates to instructions that the branch prediction resources are capable of predicting.

If no program-flow prediction resources are implemented, Arm recommends that the counter counts all branches that are not taken.

PMCEID0\_EL0[16] reads as 1 if this event is implemented and 0 otherwise.
