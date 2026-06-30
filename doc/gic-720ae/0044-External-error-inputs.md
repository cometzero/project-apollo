# External error inputs

Source: <https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/External-error-inputs>

### External error inputs

Each GIC block has generic fault inputs that allow the SoC integrator to connect and flag external faults to the FMU.

For instance, an SoC integrator might have an external safety mechanism that is physically located next to a GIC block. The SoC integrator can connect the fault signal from this external SM to the ext\_err\_req1 or ext\_err\_req0 input signals of the GIC block. If a fault occurs, the GIC flags and reports a fault in the same manner it does with internal faults.

All GIC blocks have 2 external error interfaces, but a CPUIF block can have 1-8 external error interfaces, depending on the setting of the `NUM_EXT_ERR_IF` build-time option.

A captured fault is reported in the GIC block error record with a SM\_EXT<n>\_<BLKTYPE> protection name such as SM\_EXT0\_GICD or SM\_EXT1\_ITS.
