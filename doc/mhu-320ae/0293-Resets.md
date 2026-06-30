# Resets

Source: <https://developer.arm.com/documentation/107612/0001/Functional-safety-features-of-MHU-320AE/Resets>

### Resets

MHU-320AE uses active-LOW duplicated resets. The two duplicated resets must change on the same clock edge, although MHU-320AE has an allowed skew tolerance after synchronizing the two resets, before a reset error is generated.

MHU-320AE only enters reset when both duplicated resets are asserted.

MHU-320AE exits reset when either duplicated reset deasserts.

The MHU-320AE has a reset synchronizer, so that on reset the post-synchronizer reset signals assert asynchronously and deasserts synchronously.

Although the FMU resides in the either the sender or receiver MHU block, the FMU has separate fmu\_reset\_n and fmu\_reset\_n\_chk signals. Therefore, the MHU can be reset without resetting the FMU, which enables retention of the FMU error records.
