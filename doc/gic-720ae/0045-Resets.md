# Resets

Source: <https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/Resets>

### Resets

GIC-720AE uses active-LOW duplicated resets. The two duplicated resets must change on the same clock edge, although GIC-720AE has an allowed skew tolerance after synchronizing the two resets, before a reset error is generated.

GIC-720AE only enters reset when both duplicated resets are asserted.

GIC-720AE exits reset when either duplicated reset deasserts.

The GIC-720AE has a reset synchronizer, so that on reset the post-synchronizer reset signals assert asynchronously and deasserts synchronously.

Although the FMU resides in the GICD domain, the FMU has separate fmu\_reset\_n and fmu\_reset\_n\_chk signals. Therefore, the GIC can be reset without resetting the FMU, which enables retention of the FMU error records.
